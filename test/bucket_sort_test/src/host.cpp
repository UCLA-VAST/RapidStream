#include <algorithm>
#include <iostream>
#include <fstream>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <vector>
#include <cmath>

#include "xcl2.hpp"

#define BUCKET_NUM 4
#define NO_ELEM 40960

//HBM Banks requirements
#define MAX_HBM_BANKCOUNT 32
#define BANK_NAME(n) n | XCL_MEM_TOPOLOGY
const int bank[MAX_HBM_BANKCOUNT] = {
    BANK_NAME(0),  BANK_NAME(1),  BANK_NAME(2),  BANK_NAME(3),  BANK_NAME(4),
    BANK_NAME(5),  BANK_NAME(6),  BANK_NAME(7),  BANK_NAME(8),  BANK_NAME(9),
    BANK_NAME(10), BANK_NAME(11), BANK_NAME(12), BANK_NAME(13), BANK_NAME(14),
    BANK_NAME(15), BANK_NAME(16), BANK_NAME(17), BANK_NAME(18), BANK_NAME(19),
    BANK_NAME(20), BANK_NAME(21), BANK_NAME(22), BANK_NAME(23), BANK_NAME(24),
    BANK_NAME(25), BANK_NAME(26), BANK_NAME(27), BANK_NAME(28), BANK_NAME(29),
    BANK_NAME(30), BANK_NAME(31)};


int main (int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <XCLBIN> \n", argv[0]);
        return -1;
    }

    int dataSize = NO_ELEM;

    std::string binaryFile = argv[1];

    std::vector<uint32_t, aligned_allocator<uint32_t>> source_in[BUCKET_NUM];
    std::vector<uint32_t, aligned_allocator<uint32_t>> source_out[BUCKET_NUM];

    for (int i = 0; i < BUCKET_NUM; i++) {
        source_in[i].resize(dataSize);
        source_out[i].resize(dataSize);
    }

    // create the test data
    for (int i = 0; i < BUCKET_NUM; i++) {
        for (int j = 0; j < BUCKET_NUM; j++) {
            for (int k = 0; k < NO_ELEM/BUCKET_NUM; k++) {
                source_in[i][j*NO_ELEM/BUCKET_NUM + k] = (j*BUCKET_NUM+i)*NO_ELEM/BUCKET_NUM + k;
            }
        }
    }

    /*
    for (int i = 0; i < BUCKET_NUM; i++) {
        std::random_shuffle (source_in[i].begin(), source_in[i].end() );
    }
    */

    // check input data
    std::ofstream inFILE[BUCKET_NUM];
    for (int i = 0; i < BUCKET_NUM; i++) {
        inFILE[i].open("infile" + std::to_string(i));
        for (int j = 0; j < dataSize; j++) {
            inFILE[i] << source_in[i][j] << std::endl;
        }
        inFILE[i].close();
    }


    // OPENCL HOST CODE AREA START
    cl_int err;
    auto devices = xcl::get_xil_devices();
    cl::Device device = devices[0]; // change devices[X] to the desired device

    OCL_CHECK(err, cl::Context context(device, NULL, NULL, NULL, &err));
    OCL_CHECK(err, cl::CommandQueue q(context, device, CL_QUEUE_PROFILING_ENABLE, &err));
    OCL_CHECK(err, std::string device_name = device.getInfo<CL_DEVICE_NAME>(&err));

    // Create Program
    auto fileBuf = xcl::read_binary_file(binaryFile);
    cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
    OCL_CHECK(err, cl::Program program(context, {device}, bins, NULL, &err));
    OCL_CHECK(err, cl::Kernel bucket_sort_kernel(program, "bucket_sort", &err));

    // Allocate Buffer in Global Memory: user has to use cl_mem_ext_ptr_t
    // and provide the Banks
    std::vector<cl_mem_ext_ptr_t> inBufExt(BUCKET_NUM);
    std::vector<cl_mem_ext_ptr_t> outBufExt(BUCKET_NUM);

    std::vector<cl::Buffer> buffer_input(BUCKET_NUM);
    std::vector<cl::Buffer> buffer_output(BUCKET_NUM);

    for (int i = 0; i < BUCKET_NUM; i++) {
        inBufExt[i].obj = source_in[i].data();
        inBufExt[i].param = 0;
        inBufExt[i].flags = bank[i];

        outBufExt[i].obj = source_out[i].data();
        outBufExt[i].param = 0;
        outBufExt[i].flags = bank[i+BUCKET_NUM];
    }

    // These commands will allocate memory on the FPGA. The cl::Buffer objects can
    // be used to reference the memory locations on the device.
    //Creating Buffers
    for (int i = 0; i < BUCKET_NUM; i++) {
        OCL_CHECK(err,
                  buffer_input[i] =
                      cl::Buffer(context,
                                 CL_MEM_READ_ONLY | CL_MEM_EXT_PTR_XILINX |
                                     CL_MEM_USE_HOST_PTR,
                                 sizeof(uint32_t) * dataSize,
                                 &inBufExt[i],
                                 &err));

        OCL_CHECK(err,
                  buffer_output[i] =
                      cl::Buffer(context,
                                 CL_MEM_WRITE_ONLY | CL_MEM_EXT_PTR_XILINX |
                                     CL_MEM_USE_HOST_PTR,
                                 sizeof(uint32_t) * dataSize,
                                 &outBufExt[i],
                                 &err));
    }

    // set scalar arguments
    for (int i = 0; i < BUCKET_NUM; i++) {
        OCL_CHECK(err, err = bucket_sort_kernel.setArg(i, buffer_input[i]));
    }
    for (int i = 0; i < BUCKET_NUM; i++) {
        OCL_CHECK(err, err = bucket_sort_kernel.setArg(i+BUCKET_NUM, buffer_output[i]));
    }
    OCL_CHECK(err, err = bucket_sort_kernel.setArg(2*BUCKET_NUM, dataSize));


    cl::Event krnlEvent;

    uint64_t krnl_start, krnl_end;
    double krnl_exec_time;
    double krnl_throughput;

    // copy input data to device global memory
    for (int i = 0; i < BUCKET_NUM; i++) {
        OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_input[i]},0/* 0 means from host*/));
    }
    OCL_CHECK(err, err = q.finish());
    std::cout << "Copy data from host to FPGA is done!" << std::endl;

    // Launch the kernel
    OCL_CHECK(err, err = q.enqueueTask(bucket_sort_kernel, NULL, &krnlEvent));
    clWaitForEvents(1, (const cl_event*) &krnlEvent);
    std::cout << "Kernel execution is done!" << std::endl;

    // Copy output length back to host local memory
    for (int i = 0; i < BUCKET_NUM; i++) {
        OCL_CHECK(err, err = q.enqueueMigrateMemObjects({buffer_output[i]}, CL_MIGRATE_MEM_OBJECT_HOST));
    }
    OCL_CHECK(err, err = q.finish());

    krnlEvent.getProfilingInfo(CL_PROFILING_COMMAND_START, &krnl_start);
    krnlEvent.getProfilingInfo(CL_PROFILING_COMMAND_END, &krnl_end);


    // check results
    int check_status = 0;
    for (unsigned int i = 0; i < BUCKET_NUM; i++) {
        for (int j = 0; j < dataSize; j++) {
            if ((source_out[i][j] >= (i+1) * NO_ELEM) ||  source_out[i][j] < i * NO_ELEM) {
                std::cout<< "group " << i << " element " << j << " : " << source_out[i][j] << "is out of range\n";
                check_status = 1;
                break;
            }
        }
    }

    // write output data
    std::ofstream outFILE[BUCKET_NUM];
    for (int i = 0; i < BUCKET_NUM; i++) {
        outFILE[i].open("outfile" + std::to_string(i));
        for (int j = 0; j < dataSize; j++) {
            outFILE[i] << (unsigned int)source_out[i][j] << std::endl;
        }
        outFILE[i].close();
    }

    // Calculate compression throughput & compression ratio
    krnl_exec_time = (krnl_end - krnl_start) / 1000000000.0;
    std::cout << "kernel execution time is " << krnl_exec_time << "s\n";
    krnl_throughput = (sizeof(uint32_t) * dataSize / 1024.0 / 1024.0 / 1024.0) / krnl_exec_time; 
    std::cout << "Kernel throughput is " << krnl_throughput << "GB/s" << std::endl;

    // 
    std::cout << "TEST " << (check_status ? "FAILED" : "PASSED") << std::endl;

    return EXIT_SUCCESS;
}