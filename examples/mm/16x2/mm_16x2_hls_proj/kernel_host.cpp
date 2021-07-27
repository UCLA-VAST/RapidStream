#include <assert.h>
#include <stdio.h>
#include "kernel_kernel.h"

#include "kernel.h"

int main(int argc, char **argv){
  // declarations
//  data_t cin[I][R + K - 1][C + K - 1];
//  data_t w[O][I][K][K];
//  data_t cout[O][R][C];
//  data_t cout_golden[O][R][C];
  static data_t cin[R + K - 1][C + K - 1][I];
  static data_t w[O][K][K][I];
  static data_t cout[R][C][O];
  static data_t cout_golden[R][C][O];

  // data initialization
  for (int i = 0 ; i < I; i++)
    for (int r = 0; r < R + K - 1; r++)
      for (int c = 0; c < C + K - 1; c++) {
        cin[r][c][i] = 1;
      }

  for (int o = 0; o < O; o++)
    for (int i = 0; i < I; i++) 
      for (int p = 0; p < K; p++)
        for (int q = 0; q < K; q++) {
          w[o][p][q][i] = 1;
        }
 
  {
    // Allocate memory in host memory
    float *dev_cin_unserialized = (float *)malloc((62) * (58) * (512) * sizeof(float));
    float *dev_cin = (float *)malloc(22020096 * sizeof(float));
    float *dev_cout_unserialized = (float *)malloc((60) * (56) * (512) * sizeof(float));
    float *dev_cout = (float *)malloc(1720320 * sizeof(float));
    float *dev_w_unserialized = (float *)malloc((512) * (3) * (3) * (512) * sizeof(float));
    float *dev_w = (float *)malloc(56623104 * sizeof(float));

    // Initialize host buffers
    memcpy(dev_cin_unserialized, cin, (62) * (58) * (512) * sizeof(float));
    memcpy(dev_cout_unserialized, cout, (60) * (56) * (512) * sizeof(float));
    memcpy(dev_w_unserialized, w, (512) * (3) * (3) * (512) * sizeof(float));
    host_serialize_cin(dev_cin, dev_cin_unserialized);
    host_serialize_w(dev_w, dev_w_unserialized);

    // Allocate buffers in device memory
    std::vector<cin_t16 *> buffer_cin;
    std::vector<cout_t16 *> buffer_cout;
    std::vector<w_t16 *> buffer_w;
    for (int i = 0; i < 1; i++) {
      cin_t16 *buffer_cin_tmp = (cin_t16 *)malloc((22020096) * sizeof(float));
      buffer_cin.push_back(buffer_cin_tmp);
    }
    for (int i = 0; i < 1; i++) {
      cout_t16 *buffer_cout_tmp = (cout_t16 *)malloc((1720320) * sizeof(float));
      buffer_cout.push_back(buffer_cout_tmp);
    }
    for (int i = 0; i < 1; i++) {
      w_t16 *buffer_w_tmp = (w_t16 *)malloc((56623104) * sizeof(float));
      buffer_w.push_back(buffer_w_tmp);
    }

    for (int i = 0; i < 1; i++) {
      memcpy(buffer_cin[i], dev_cin, (22020096) * sizeof(float));
    }

    for (int i = 0; i < 1; i++) {
      memcpy(buffer_w[i], dev_w, (56623104) * sizeof(float));
    }

    {
      // Launch the kernel
      kernel0(buffer_cin[0], buffer_cout[0], buffer_w[0]);
    }
    for (int i = 0; i < 1; i++) {
      memcpy(dev_cout, buffer_cout[i], (1720320) * sizeof(float));
    }

    host_deserialize_cout(dev_cout_unserialized, dev_cout);
    // Restore data from host buffers
    memcpy(cout, dev_cout_unserialized, (60) * (56) * (512) * sizeof(float));

    // Clean up resources
    for (int i = 0; i < 1; i++) {
      free(buffer_cin[i]);
    }
    for (int i = 0; i < 1; i++) {
      free(buffer_cout[i]);
    }
    for (int i = 0; i < 1; i++) {
      free(buffer_w[i]);
    }
    free(dev_cin);
    free(dev_cin_unserialized);
    free(dev_cout);
    free(dev_cout_unserialized);
    free(dev_w);
    free(dev_w_unserialized);
  }
 
  for (int o = 0; o < O; o++)
    for (int r = 0; r < R; r++)
      for (int c = 0; c < C; c++) {
        cout_golden[r][c][o] = 0;
        for (int i = 0; i < I; i++)
          for (int p = 0; p < 3; p++)
            for (int q = 0; q < 3; q++) {
              cout_golden[r][c][o] = cout_golden[r][c][o] + cin[r + p][c + q][i] * w[o][p][q][i];
            }
      }

  int err = 0;
  float thres = 0.001;
  for (int o = 0; o < O; o++)
    for (int r = 0; r < R; r++)
      for (int c = 0; c < C; c++) {
        if (fabs((float)cout_golden[r][c][o] - (float)cout[r][c][o]) > thres) {
          err++;
        }
      }

  if (err) {
    printf("Test failed with %d errors!\n", err);
    return -1;
  } else {
    printf("Test passed!\n");
    return 0;
  }
}
