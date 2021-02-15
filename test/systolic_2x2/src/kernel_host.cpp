#include "kernel_host.hpp"
#include <assert.h>
#include <stdio.h>
#include "kernel.h"

int main(int argc, char **argv) {
  data_t A[I][K], B[J][K], C[I][J], C_golden[I][J]; // gemm0,3
  //data_t A[I][K], B[K][J], C[I][J], C_golden[I][J]; // gemm0,3

  for (int i = 0; i < I; i++) 
    for (int k = 0; k < K; k++) {
      A[i][k] = (data_t)rand() / RAND_MAX;
    }

  for (int j = 0; j < J; j++)
    for (int k = 0; k < K; k++) {
      B[j][k] = (data_t)rand() / RAND_MAX;
      //B[k][j] = (data_t)rand() / RAND_MAX;
    }

  {
    if (argc != 2) {
      std::cout << "Usage: " << argv[0] << " <XCLBIN File>" << std::endl;
      return EXIT_FAILURE;
    }

    cl_int err;
    std::vector<cl::Device> devices = get_devices();
//    cl::Device device = devices[1];
    cl::Device device = devices[0];
    std::string device_name = device.getInfo<CL_DEVICE_NAME>();
    std::cout << "Found Device=" << device_name.c_str() << std::endl;
    // Creating Context and Command Queue for selected device
    cl::Context context(device);
    cl::CommandQueue q(context, device);
    // Import XCLBIN
    xclbin_file_name = argv[1];
    cl::Program::Binaries kernel_bins = import_binary_file();
    // Create Program and Kernel
//    devices.erase(devices.begin());
    devices.resize(1);
    cl::Program program(context, devices, kernel_bins);
    cl::Kernel krnl(program, "kernel0");

    // Allocate memory in host memory
    std::vector<float, aligned_allocator<float>> dev_A_unserialized((64) * (64));
    std::vector<float, aligned_allocator<float>> dev_A(16384);
    std::vector<float, aligned_allocator<float>> dev_B_unserialized((64) * (64));
    std::vector<float, aligned_allocator<float>> dev_B(16384);
    std::vector<float, aligned_allocator<float>> dev_C_unserialized((64) * (64));
    std::vector<float, aligned_allocator<float>> dev_C(4096);

    // Initialize host buffers
    std::copy(reinterpret_cast<float *>(A), reinterpret_cast<float *>(A) + (64) * (64), dev_A_unserialized.begin());
    std::copy(reinterpret_cast<float *>(B), reinterpret_cast<float *>(B) + (64) * (64), dev_B_unserialized.begin());
    std::copy(reinterpret_cast<float *>(C), reinterpret_cast<float *>(C) + (64) * (64), dev_C_unserialized.begin());
    host_serialize_A(dev_A, dev_A_unserialized);
    host_serialize_B(dev_B, dev_B_unserialized);

    // Allocate buffers in device memory
    // Buffers are allocated using CL_MEM_USE_HOST_PTR for efficient memory and
    // device-to-host communication
    std::vector<cl::Buffer> buffer_A;
    std::vector<cl::Buffer> buffer_B;
    std::vector<cl::Buffer> buffer_C;
    for (int i = 0; i < 1; i++) {
      OCL_CHECK(err,
                cl::Buffer buffer_A_tmp(context,
                                        CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY,
                                        (16384) * sizeof(float),
                                        dev_A.data(),
                                        &err));
      buffer_A.push_back(std::move(buffer_A_tmp));
    }
    for (int i = 0; i < 1; i++) {
      OCL_CHECK(err,
                cl::Buffer buffer_B_tmp(context,
                                        CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY,
                                        (16384) * sizeof(float),
                                        dev_B.data(),
                                        &err));
      buffer_B.push_back(std::move(buffer_B_tmp));
    }
    for (int i = 0; i < 1; i++) {
      OCL_CHECK(err,
                cl::Buffer buffer_C_tmp(context,
                                        CL_MEM_USE_HOST_PTR | CL_MEM_WRITE_ONLY,
                                        (4096) * sizeof(float),
                                        dev_C.data(),
                                        &err));
      buffer_C.push_back(std::move(buffer_C_tmp));
    }

    auto host_begin = std::chrono::high_resolution_clock::now();
    auto fpga_begin = std::chrono::high_resolution_clock::now();
    auto fpga_end = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < 1; i++) {
      OCL_CHECK(err,
                err = q.enqueueMigrateMemObjects({buffer_A[i]}, 0));
    }

    for (int i = 0; i < 1; i++) {
      OCL_CHECK(err,
                err = q.enqueueMigrateMemObjects({buffer_B[i]}, 0));
    }

    {
      OCL_CHECK(err, err = krnl.setArg(0, buffer_A[0]));
      OCL_CHECK(err, err = krnl.setArg(1, buffer_B[0]));
      OCL_CHECK(err, err = krnl.setArg(2, buffer_C[0]));
      q.finish();

      //// Warm up
      //OCL_CHECK(err, err = q.enqueueTask(krnl));
      //q.finish();

      fpga_begin = std::chrono::high_resolution_clock::now();

      // Launch the kernel
      for (int i = 0; i < 1; i++)
        OCL_CHECK(err, err = q.enqueueTask(krnl));

      q.finish();
      fpga_end = std::chrono::high_resolution_clock::now();
    }

    for (int i = 0; i < 1; i++) {
      OCL_CHECK(err,
                err = q.enqueueMigrateMemObjects({buffer_C[i]}, CL_MIGRATE_MEM_OBJECT_HOST));
    }
    q.finish();
    auto host_end = std::chrono::high_resolution_clock::now();

    // Calculate time
    std::chrono::duration<double> fpga_duration = fpga_end - fpga_begin;
    std::cout << "FPGA Time: " << fpga_duration.count() / 1 << " s" << std::endl;
    std::chrono::duration<double> host_duration = host_end - host_begin;
    std::cout << "Host Time: " << host_duration.count() << " s" << std::endl;

    host_deserialize_C(dev_C_unserialized, dev_C);
    // Restore data from host buffers
    std::copy(dev_C_unserialized.begin(), dev_C_unserialized.end(), reinterpret_cast<float *>(C));
  }

//#pragma scop
//  for (int i = 0; i < I; i++) 
//    for (int j = 0; j < J; j++) {
//      float sum = 0;
//      for (int k = 0; k < K; k++) {
//        sum = (A[i][k] * B[j][k]) + sum;
//      }
//      C[i][j] = sum;
//    }
//#pragma endscop

  for (int i = 0; i < I; i++)
    for (int j = 0; j < J; j++) {
      C_golden[i][j] = 0;
      for (int k = 0; k < K; k++) {
        C_golden[i][j] = C_golden[i][j] + A[i][k] * B[j][k];
      }
    }

  int err = 0;
  for (int i = 0; i < I; i++)
    for (int j = 0; j < J; j++) {
      if (fabs((float)C_golden[i][j] - (float)C[i][j]) > 0.001)
        err++;
    }

  if (err)
    printf("Failed with %d errors!\n", err);
  else
    printf("Passed!\n");

  return 0;
}
