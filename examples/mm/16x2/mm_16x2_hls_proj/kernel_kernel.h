#include <ap_int.h>
#include <hls_stream.h>

#define min(x,y) ((x < y) ? x : y)
#define max(x,y) ((x > y) ? x : y)

/* Data Type */
typedef float cin_t1;
typedef float cout_t1;
typedef float w_t1;
typedef ap_uint<512> cin_t16;
typedef ap_uint<256> cin_t8;
typedef ap_uint<512> cout_t16;
typedef ap_uint<64> cout_t2;
typedef ap_uint<512> w_t16;
typedef ap_uint<256> w_t8;
/* Data Type */

/* Helper Function */
inline void host_serialize_cin(float *cin_to, float *cin_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 7; c0 += 1)
    for (int c1 = 0; c1 <= 5; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1)
        for (int c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // io_L3
          for (int c4 = 0; c4 <= 1; c4 += 1) {
            // io_L2
            for (int c5 = 0; c5 <= 6; c5 += 1)
              for (int c6 = 0; c6 <= 15; c6 += 1)
                for (int c7 = 0; c7 <= 63; c7 += 1)
                  cin_to[cnt++] = cin_from[((10 * c1 + 5 * c4 + c5) * 58 + (14 * c2 + c6)) * 512 + (64 * c3 + c7)];
          }
        }
}
/* Helper Function */

/* Helper Function */
inline void host_serialize_w(float *w_to, float *w_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 7; c0 += 1)
    for (int c1 = 0; c1 <= 5; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1)
        for (int c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // io_L3
          for (int c4 = 0; c4 <= 15; c4 += 1) {
            // io_L2
            for (int c5 = 0; c5 <= 3; c5 += 1)
              for (int c6 = 0; c6 <= 2; c6 += 1)
                for (int c7 = 0; c7 <= 2; c7 += 1)
                  for (int c8 = 0; c8 <= 63; c8 += 1)
                    w_to[cnt++] = w_from[(((64 * c0 + 4 * c4 + c5) * 3 + c6) * 3 + c7) * 512 + (64 * c3 + c8)];
          }
        }
}
/* Helper Function */

/* Helper Function */
inline void host_deserialize_cout(float *cout_to, float *cout_from){
  /* Variable Declaration */
  unsigned int cnt = 0;
  /* Variable Declaration */

  for (int c0 = 0; c0 <= 7; c0 += 1)
    for (int c1 = 0; c1 <= 5; c1 += 1)
      for (int c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (int c4 = 0; c4 <= 1; c4 += 1) {
          // io_L2
          for (int c5 = 0; c5 <= 15; c5 += 1) {
            // io_L1
            // pe
            for (int c6 = 0; c6 <= 4; c6 += 1)
              for (int c7 = 0; c7 <= 13; c7 += 1)
                for (int c8 = 0; c8 <= 3; c8 += 1)
                  cout_to[((10 * c1 + 5 * c4 + c6) * 56 + (14 * c2 + c7)) * 512 + (64 * c0 + 4 * c5 + c8)] = cout_from[cnt++];
          }
        }
      }
}
/* Helper Function */

void kernel0(cin_t16 *cin, cout_t16 *cout, w_t16 *w);
void cin_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, int c3, cin_t8 local_cin[7][16][8], hls::stream<cin_t8> &fifo_cin_local_out, bool intra_trans_en);
void cin_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, int c3, cin_t8 local_cin[7][16][8], hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_out, bool inter_trans_en);
void cin_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, int c3, cin_t8 local_cin[7][16][8], hls::stream<cin_t8> &fifo_cin_in, bool inter_trans_en);
void w_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, int c3, w_t8 local_w[4][3][3][8], hls::stream<w_t8> &fifo_w_local_out, bool intra_trans_en);
void w_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, int c3, w_t8 local_w[4][3][3][8], hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_out, bool inter_trans_en);
void w_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, int c3, w_t8 local_w[4][3][3][8], hls::stream<w_t8> &fifo_w_in, bool inter_trans_en);
void PE_wrapper(int idx, int idy, hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_out, hls::stream<float> &fifo_cout_drain_out, hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_out);
void cout_drain_IO_L1_out_intra_trans(int idx, int idy, int c0, int c1, int c2, cout_t2 local_cout[5][14][2], hls::stream<float> &fifo_cout_drain_local_in);
void cout_drain_IO_L1_out_inter_trans(int idx, int idy, int c0, int c1, int c2, cout_t2 local_cout[5][14][2], hls::stream<cout_t2> &fifo_cout_drain_in, hls::stream<cout_t2> &fifo_cout_drain_out);
void cout_drain_IO_L1_out_inter_trans_boundary(int idx, int idy, int c0, int c1, int c2, cout_t2 local_cout[5][14][2], hls::stream<cout_t2> &fifo_cout_drain_out);
void cout_drain_IO_L1_out_wrapper(int idx, int idy, hls::stream<cout_t2> &fifo_cout_drain_in, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<float> &fifo_cout_drain_local_in);
void cout_drain_IO_L1_out_boundary_wrapper(int idx, int idy, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<float> &fifo_cout_drain_local_in);
