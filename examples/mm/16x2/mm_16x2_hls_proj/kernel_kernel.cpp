#include "kernel_kernel.h"
/* Module Definition */
void cin_IO_L3_in(hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
        for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // io_L3
          for (ap_uint<2> c4 = 0; c4 <= 1; c4 += 1) {
            // io_L2
            for (ap_uint<4> c5 = 0; c5 <= 6; c5 += 1)
              for (ap_uint<5> c6 = 0; c6 <= 15; c6 += 1) {
                // access_coalesce
                // access_serialize
                for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1) {
                #pragma HLS PIPELINE II=1
                  {
                    cin_t8 in_data;
                    cin_t8 out_data;
                    in_data = fifo_cin_in.read();
                    out_data = in_data;
                    fifo_cin_local_out.write(out_data);
                  }
                }
              }
          }
        }
}
/* Module Definition */

/* Module Definition */
void cin_IO_L3_in_serialize(cin_t16 *cin, hls::stream<cin_t8> &fifo_cin_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  cin_t8 fifo_data;
  cin_t16 mem_data;
  for (ap_uint<22> i = 0; i < 1376256; i++) {
  #pragma HLS PIPELINE II=1
    mem_data = cin[i];
    for (ap_uint<2> p = 0; p < 2; p++) {
      fifo_data = mem_data(255, 0);
      mem_data = mem_data >> 256;
      fifo_cin_local_out.write(fifo_data);
    }
  }
}
/* Module Definition */

/* Module Definition */
void cin_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, int c3, cin_t8 local_cin[7][16][8], hls::stream<cin_t8> &fifo_cin_local_out, bool intra_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!intra_trans_en) return;


  // io_L2
  // io_L1
  // pe
  for (ap_uint<2> c6 = 0; c6 <= 1; c6 += 1)
    for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1)
      for (ap_uint<3> c8 = 0; c8 <= 2; c8 += 1)
        for (ap_uint<3> c9 = 0; c9 <= 2; c9 += 1) {
          // latency
          for (ap_uint<3> c10 = 0; c10 <= 3; c10 += 1) {
            // latency
            for (ap_uint<4> c11 = 0; c11 <= 4; c11 += 1) {
              // latency
              for (ap_uint<4> c12 = 0; c12 <= 6; c12 += 1) {
              #pragma HLS PIPELINE II=1
                // simd
                {
                  cin_t8 in_data;
                  cin_t8 out_data;
                  in_data = local_cin[c11 + c8][c12 + 7*c6 + c9][c7];
                  out_data = in_data;
                  fifo_cin_local_out.write(out_data);
                }
              }
            }
          }
        }
}
/* Module Definition */

/* Module Definition */
void cin_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, int c3, cin_t8 local_cin[7][16][8], hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_out, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (ap_uint<2> c4 = p0; c4 <= 1; c4 += 1) {
    // io_L2
    if (c4 == p0) {
      for (ap_uint<4> c5 = 0; c5 <= 6; c5 += 1)
        for (ap_uint<5> c6 = 0; c6 <= 15; c6 += 1) {
          // access_coalesce
          for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1) {
          #pragma HLS PIPELINE II=1
            {
              cin_t8 in_data;
              cin_t8 out_data;
              in_data = fifo_cin_in.read();
              out_data = in_data;
              local_cin[c5][c6][c7] = out_data;
            }
          }
        }
    } else {
      for (ap_uint<4> c5 = 0; c5 <= 6; c5 += 1)
        for (ap_uint<5> c6 = 0; c6 <= 15; c6 += 1) {
          // access_coalesce
          for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1) {
          #pragma HLS PIPELINE II=1
            {
              cin_t8 in_data;
              cin_t8 out_data;
              in_data = fifo_cin_in.read();
              out_data = in_data;
              fifo_cin_out.write(out_data);
            }
          }
        }
    }
  }
}
/* Module Definition */

/* Module Definition */
void cin_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, int c3, cin_t8 local_cin[7][16][8], hls::stream<cin_t8> &fifo_cin_in, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (ap_uint<2> c4 = p0; c4 <= 1; c4 += 1)
    if (c4 == p0) {
      // io_L2
      for (ap_uint<4> c5 = 0; c5 <= 6; c5 += 1)
        for (ap_uint<5> c6 = 0; c6 <= 15; c6 += 1) {
          // access_coalesce
          for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1) {
          #pragma HLS PIPELINE II=1
            {
              cin_t8 in_data;
              cin_t8 out_data;
              in_data = fifo_cin_in.read();
              out_data = in_data;
              local_cin[c5][c6][c7] = out_data;
            }
          }
        }
    }
}
/* Module Definition */

/* Module Definition */
void cin_IO_L2_in(int idx, hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_out, hls::stream<cin_t8> &fifo_cin_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  cin_t8 local_cin_ping[7][16][8];
  #pragma HLS RESOURCE variable=local_cin_ping core=RAM_1P_BRAM
  cin_t8 local_cin_pong[7][16][8];
  #pragma HLS RESOURCE variable=local_cin_pong core=RAM_1P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  int c3, c3_prev;
  /* Variable Declaration */

  {
    for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
      for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
        for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
          for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
            // array
            // io_L3
            {
              if (arb == 0) {
                cin_IO_L2_in_inter_trans(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_cin_pong, 
                  /* fifo */ fifo_cin_in, 
                  /* fifo */ fifo_cin_out, 
                  /* enable */ inter_trans_en
                );
                cin_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_cin_ping, 
                  /* fifo */ fifo_cin_local_out, 
                  /* enable */ intra_trans_en
                );
              } else {
                cin_IO_L2_in_inter_trans(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_cin_ping, 
                  /* fifo */ fifo_cin_in, 
                  /* fifo */ fifo_cin_out, 
                  /* enable */ inter_trans_en
                );
                cin_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_cin_pong, 
                  /* fifo */ fifo_cin_local_out, 
                  /* enable */ intra_trans_en
                );
              }
              intra_trans_en = 1;
              arb = !arb;
              c0_prev = c0;
              c1_prev = c1;
              c2_prev = c2;
              c3_prev = c3;
            }
          }
    if (arb == 0) {
      cin_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_cin_ping, 
        /* fifo */ fifo_cin_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      cin_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_cin_pong, 
        /* fifo */ fifo_cin_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void cin_IO_L2_in_boundary(int idx, hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  cin_t8 local_cin_ping[7][16][8];
  #pragma HLS RESOURCE variable=local_cin_ping core=RAM_1P_BRAM
  cin_t8 local_cin_pong[7][16][8];
  #pragma HLS RESOURCE variable=local_cin_pong core=RAM_1P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  int c3, c3_prev;
  /* Variable Declaration */

  {
    for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
      for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
        for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
          for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
            // array
            // io_L3
            {
              if (arb == 0) {
                cin_IO_L2_in_inter_trans_boundary(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_cin_pong, 
                  /* fifo */ fifo_cin_in, 
                  /* enable */ inter_trans_en
                );
                cin_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_cin_ping, 
                  /* fifo */ fifo_cin_local_out, 
                  /* enable */ intra_trans_en
                );
              } else {
                cin_IO_L2_in_inter_trans_boundary(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_cin_ping, 
                  /* fifo */ fifo_cin_in, 
                  /* enable */ inter_trans_en
                );
                cin_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_cin_pong, 
                  /* fifo */ fifo_cin_local_out, 
                  /* enable */ intra_trans_en
                );
              }
              intra_trans_en = 1;
              arb = !arb;
              c0_prev = c0;
              c1_prev = c1;
              c2_prev = c2;
              c3_prev = c3;
            }
          }
    if (arb == 0) {
      cin_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_cin_ping, 
        /* fifo */ fifo_cin_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      cin_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_cin_pong, 
        /* fifo */ fifo_cin_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void w_IO_L3_in(hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
        for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // io_L3
          for (ap_uint<5> c4 = 0; c4 <= 15; c4 += 1) {
            // io_L2
            for (ap_uint<3> c5 = 0; c5 <= 3; c5 += 1)
              for (ap_uint<3> c6 = 0; c6 <= 2; c6 += 1)
                for (ap_uint<3> c7 = 0; c7 <= 2; c7 += 1) {
                  // access_coalesce
                  // access_serialize
                  for (ap_uint<4> c8 = 0; c8 <= 7; c8 += 1) {
                  #pragma HLS PIPELINE II=1
                    {
                      w_t8 in_data;
                      w_t8 out_data;
                      in_data = fifo_w_in.read();
                      out_data = in_data;
                      fifo_w_local_out.write(out_data);
                    }
                  }
                }
          }
        }
}
/* Module Definition */

/* Module Definition */
void w_IO_L3_in_serialize(w_t16 *w, hls::stream<w_t8> &fifo_w_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  w_t8 fifo_data;
  w_t16 mem_data;
  for (ap_uint<23> i = 0; i < 3538944; i++) {
  #pragma HLS PIPELINE II=1
    mem_data = w[i];
    for (ap_uint<2> p = 0; p < 2; p++) {
      fifo_data = mem_data(255, 0);
      mem_data = mem_data >> 256;
      fifo_w_local_out.write(fifo_data);
    }
  }
}
/* Module Definition */

/* Module Definition */
void w_IO_L2_in_intra_trans(int idx, int c0, int c1, int c2, int c3, w_t8 local_w[4][3][3][8], hls::stream<w_t8> &fifo_w_local_out, bool intra_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!intra_trans_en) return;


  // io_L2
  // io_L1
  // pe
  for (ap_uint<2> c6 = 0; c6 <= 1; c6 += 1)
    for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1)
      for (ap_uint<3> c8 = 0; c8 <= 2; c8 += 1)
        for (ap_uint<3> c9 = 0; c9 <= 2; c9 += 1) {
          // latency
          for (ap_uint<3> c10 = 0; c10 <= 3; c10 += 1) {
            // latency
            for (ap_uint<4> c11 = 0; c11 <= 4; c11 += 1) {
              // latency
              for (ap_uint<4> c12 = 0; c12 <= 6; c12 += 1) {
              #pragma HLS PIPELINE II=1
                // simd
                {
                  w_t8 in_data;
                  w_t8 out_data;
                  in_data = local_w[c10][c8][c9][c7];
                  out_data = in_data;
                  fifo_w_local_out.write(out_data);
                }
              }
            }
          }
        }
}
/* Module Definition */

/* Module Definition */
void w_IO_L2_in_inter_trans(int idx, int c0, int c1, int c2, int c3, w_t8 local_w[4][3][3][8], hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_out, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (ap_uint<5> c4 = p0; c4 <= 15; c4 += 1) {
    // io_L2
    if (c4 == p0) {
      for (ap_uint<3> c5 = 0; c5 <= 3; c5 += 1)
        for (ap_uint<3> c6 = 0; c6 <= 2; c6 += 1)
          for (ap_uint<3> c7 = 0; c7 <= 2; c7 += 1) {
            // access_coalesce
            for (ap_uint<4> c8 = 0; c8 <= 7; c8 += 1) {
            #pragma HLS PIPELINE II=1
              {
                w_t8 in_data;
                w_t8 out_data;
                in_data = fifo_w_in.read();
                out_data = in_data;
                local_w[c5][c6][c7][c8] = out_data;
              }
            }
          }
    } else {
      for (ap_uint<3> c5 = 0; c5 <= 3; c5 += 1)
        for (ap_uint<3> c6 = 0; c6 <= 2; c6 += 1)
          for (ap_uint<3> c7 = 0; c7 <= 2; c7 += 1) {
            // access_coalesce
            for (ap_uint<4> c8 = 0; c8 <= 7; c8 += 1) {
            #pragma HLS PIPELINE II=1
              {
                w_t8 in_data;
                w_t8 out_data;
                in_data = fifo_w_in.read();
                out_data = in_data;
                fifo_w_out.write(out_data);
              }
            }
          }
    }
  }
}
/* Module Definition */

/* Module Definition */
void w_IO_L2_in_inter_trans_boundary(int idx, int c0, int c1, int c2, int c3, w_t8 local_w[4][3][3][8], hls::stream<w_t8> &fifo_w_in, bool inter_trans_en) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  if (!inter_trans_en) return;

  for (ap_uint<5> c4 = p0; c4 <= 15; c4 += 1)
    if (c4 == p0) {
      // io_L2
      for (ap_uint<3> c5 = 0; c5 <= 3; c5 += 1)
        for (ap_uint<3> c6 = 0; c6 <= 2; c6 += 1)
          for (ap_uint<3> c7 = 0; c7 <= 2; c7 += 1) {
            // access_coalesce
            for (ap_uint<4> c8 = 0; c8 <= 7; c8 += 1) {
            #pragma HLS PIPELINE II=1
              {
                w_t8 in_data;
                w_t8 out_data;
                in_data = fifo_w_in.read();
                out_data = in_data;
                local_w[c5][c6][c7][c8] = out_data;
              }
            }
          }
    }
}
/* Module Definition */

/* Module Definition */
void w_IO_L2_in(int idx, hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_out, hls::stream<w_t8> &fifo_w_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  w_t8 local_w_ping[4][3][3][8];
  #pragma HLS RESOURCE variable=local_w_ping core=RAM_1P_BRAM
  w_t8 local_w_pong[4][3][3][8];
  #pragma HLS RESOURCE variable=local_w_pong core=RAM_1P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  int c3, c3_prev;
  /* Variable Declaration */

  {
    for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
      for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
        for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
          for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
            // array
            // io_L3
            {
              if (arb == 0) {
                w_IO_L2_in_inter_trans(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_w_pong, 
                  /* fifo */ fifo_w_in, 
                  /* fifo */ fifo_w_out, 
                  /* enable */ inter_trans_en
                );
                w_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_w_ping, 
                  /* fifo */ fifo_w_local_out, 
                  /* enable */ intra_trans_en
                );
              } else {
                w_IO_L2_in_inter_trans(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_w_ping, 
                  /* fifo */ fifo_w_in, 
                  /* fifo */ fifo_w_out, 
                  /* enable */ inter_trans_en
                );
                w_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_w_pong, 
                  /* fifo */ fifo_w_local_out, 
                  /* enable */ intra_trans_en
                );
              }
              intra_trans_en = 1;
              arb = !arb;
              c0_prev = c0;
              c1_prev = c1;
              c2_prev = c2;
              c3_prev = c3;
            }
          }
    if (arb == 0) {
      w_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_w_ping, 
        /* fifo */ fifo_w_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      w_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_w_pong, 
        /* fifo */ fifo_w_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void w_IO_L2_in_boundary(int idx, hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_local_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  w_t8 local_w_ping[4][3][3][8];
  #pragma HLS RESOURCE variable=local_w_ping core=RAM_1P_BRAM
  w_t8 local_w_pong[4][3][3][8];
  #pragma HLS RESOURCE variable=local_w_pong core=RAM_1P_BRAM
  bool arb = 0;
  bool inter_trans_en = 1;
  bool intra_trans_en = 0;
  int c0, c0_prev;
  int c1, c1_prev;
  int c2, c2_prev;
  int c3, c3_prev;
  /* Variable Declaration */

  {
    for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
      for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
        for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
          for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
            // array
            // io_L3
            {
              if (arb == 0) {
                w_IO_L2_in_inter_trans_boundary(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_w_pong, 
                  /* fifo */ fifo_w_in, 
                  /* enable */ inter_trans_en
                );
                w_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_w_ping, 
                  /* fifo */ fifo_w_local_out, 
                  /* enable */ intra_trans_en
                );
              } else {
                w_IO_L2_in_inter_trans_boundary(
                  /* module id */ idx, 
                  /* host iter */ c0, 
                  /* host iter */ c1, 
                  /* host iter */ c2, 
                  /* host iter */ c3, 
                  /* array */ local_w_ping, 
                  /* fifo */ fifo_w_in, 
                  /* enable */ inter_trans_en
                );
                w_IO_L2_in_intra_trans(
                  /* module id */ idx, 
                  /* host iter */ c0_prev, 
                  /* host iter */ c1_prev, 
                  /* host iter */ c2_prev, 
                  /* host iter */ c3_prev, 
                  /* array */ local_w_pong, 
                  /* fifo */ fifo_w_local_out, 
                  /* enable */ intra_trans_en
                );
              }
              intra_trans_en = 1;
              arb = !arb;
              c0_prev = c0;
              c1_prev = c1;
              c2_prev = c2;
              c3_prev = c3;
            }
          }
    if (arb == 0) {
      w_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_w_ping, 
        /* fifo */ fifo_w_local_out, 
        /* enable */ intra_trans_en
      );
    } else {
      w_IO_L2_in_intra_trans(
        /* module id */ idx, 
        /* host iter */ c0_prev, 
        /* host iter */ c1_prev, 
        /* host iter */ c2_prev, 
        /* host iter */ c3_prev, 
        /* array */ local_w_pong, 
        /* fifo */ fifo_w_local_out, 
        /* enable */ intra_trans_en
      );
    }
  }
}
/* Module Definition */

/* Module Definition */
void PE(int idx, int idy, hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_out, hls::stream<float> &fifo_cout_drain_out, hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_out) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  cin_t1 local_cin[1][1][8];
  #pragma HLS ARRAY_PARTITION variable=local_cin dim=0 complete
  cout_t1 local_cout[5][14][4];
  #pragma HLS RESOURCE variable=local_cout core=RAM_2P_BRAM
  w_t1 local_w[1][1][1][8];
  #pragma HLS ARRAY_PARTITION variable=local_w dim=0 complete
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1)
        for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // pe
          for (ap_uint<2> c6 = 0; c6 <= 1; c6 += 1) {
            if (c3 == 0) {
              // latency
              for (ap_uint<3> c8 = 0; c8 <= 3; c8 += 1) {
                // latency
                for (ap_uint<4> c9 = 0; c9 <= 4; c9 += 1) {
                  // latency
                  for (ap_uint<4> c10 = 0; c10 <= 6; c10 += 1) {
                  #pragma HLS PIPELINE II=1
                    // simd
                    // hls_unroll
                    local_cout[c9][c10 + 7*c6][c8] = 0;
                  }
                }
              }
            }
            for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1)
              for (ap_uint<3> c8 = 0; c8 <= 2; c8 += 1)
                for (ap_uint<3> c9 = 0; c9 <= 2; c9 += 1) {
                  // latency
                  for (ap_uint<3> c10 = 0; c10 <= 3; c10 += 1) {
                    // latency
                    for (ap_uint<4> c11 = 0; c11 <= 4; c11 += 1) {
                      // latency
                      for (ap_uint<4> c12 = 0; c12 <= 6; c12 += 1) {
                      #pragma HLS PIPELINE II=1
                        {
                          {
                            cin_t8 fifo_data;
                            fifo_data = fifo_cin_in.read();
                            for (ap_uint<4> n = 0; n < 8; n++) {
                            #pragma HLS UNROLL
                              union {unsigned int ui; float ut;} u;
                              u.ui = (unsigned int)fifo_data(31, 0);
                              local_cin[0][0][n] = u.ut;
                              fifo_data = fifo_data >> 32;
                            }
                          }
                          {
                            w_t8 fifo_data;
                            fifo_data = fifo_w_in.read();
                            for (ap_uint<4> n = 0; n < 8; n++) {
                            #pragma HLS UNROLL
                              union {unsigned int ui; float ut;} u;
                              u.ui = (unsigned int)fifo_data(31, 0);
                              local_w[0][0][0][n] = u.ut;
                              fifo_data = fifo_data >> 32;
                            }
                          }
                          // simd
                          for (ap_uint<4> c13 = 0; c13 <= 7; c13 += 1) {
                          #pragma HLS UNROLL
                            local_cout[c11][c12 + 7*c6][c10] = (local_cout[c11][c12 + 7*c6][c10] + (local_cin[0][0][c13] * local_w[0][0][0][c13]));
                          }
                          {
                            w_t8 fifo_data;
                            union {unsigned int ui; float ut;} u7, u6, u5, u4, u3, u2, u1, u0;
                            u7.ut = local_w[0][0][0][7];
                            u6.ut = local_w[0][0][0][6];
                            u5.ut = local_w[0][0][0][5];
                            u4.ut = local_w[0][0][0][4];
                            u3.ut = local_w[0][0][0][3];
                            u2.ut = local_w[0][0][0][2];
                            u1.ut = local_w[0][0][0][1];
                            u0.ut = local_w[0][0][0][0];
                            fifo_data = (ap_uint<32>(u7.ui), ap_uint<32>(u6.ui), ap_uint<32>(u5.ui), ap_uint<32>(u4.ui), ap_uint<32>(u3.ui), ap_uint<32>(u2.ui), ap_uint<32>(u1.ui), ap_uint<32>(u0.ui));
                            fifo_w_out.write(fifo_data);
                          }
                          if (c3 == 7 && c7 == 7 && c8 == 2 && c9 == 2)
                            fifo_cout_drain_out.write(local_cout[c11][c12 + 7*c6][c10]);
                          {
                            cin_t8 fifo_data;
                            union {unsigned int ui; float ut;} u7, u6, u5, u4, u3, u2, u1, u0;
                            u7.ut = local_cin[0][0][7];
                            u6.ut = local_cin[0][0][6];
                            u5.ut = local_cin[0][0][5];
                            u4.ut = local_cin[0][0][4];
                            u3.ut = local_cin[0][0][3];
                            u2.ut = local_cin[0][0][2];
                            u1.ut = local_cin[0][0][1];
                            u0.ut = local_cin[0][0][0];
                            fifo_data = (ap_uint<32>(u7.ui), ap_uint<32>(u6.ui), ap_uint<32>(u5.ui), ap_uint<32>(u4.ui), ap_uint<32>(u3.ui), ap_uint<32>(u2.ui), ap_uint<32>(u1.ui), ap_uint<32>(u0.ui));
                            fifo_cin_out.write(fifo_data);
                          }
                        }
                      }
                    }
                  }
                }
          }
        }
}
/* Module Definition */

/* Module Definition */
void PE_wrapper(int idx, int idy, hls::stream<cin_t8> &fifo_cin_in, hls::stream<cin_t8> &fifo_cin_out, hls::stream<float> &fifo_cout_drain_out, hls::stream<w_t8> &fifo_w_in, hls::stream<w_t8> &fifo_w_out)
 {
  PE(
    /* module id */ idx, 
    /* module id */ idy, 
    /* fifo */ fifo_cin_in, 
    /* fifo */ fifo_cin_out, 
    /* fifo */ fifo_cout_drain_out, 
    /* fifo */ fifo_w_in, 
    /* fifo */ fifo_w_out);
}
/* Module Definition */

/* Module Definition */
void cin_PE_dummy_in(int idx, int idy, hls::stream<cin_t8> &fifo_cin_in) {
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        {
        }
        for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // pe
          for (ap_uint<2> c6 = 0; c6 <= 1; c6 += 1)
            for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1)
              for (ap_uint<3> c8 = 0; c8 <= 2; c8 += 1)
                for (ap_uint<3> c9 = 0; c9 <= 2; c9 += 1) {
                  // latency
                  for (ap_uint<3> c10 = 0; c10 <= 3; c10 += 1) {
                    // latency
                    for (ap_uint<4> c11 = 0; c11 <= 4; c11 += 1) {
                      // latency
                      for (ap_uint<4> c12 = 0; c12 <= 6; c12 += 1) {
                      #pragma HLS PIPELINE II=1
                        cin_t8 fifo_data;
                        fifo_data = fifo_cin_in.read();
                      }
                    }
                  }
                }
        }
      }
}
/* Module Definition */

/* Module Definition */
void w_PE_dummy_in(int idx, int idy, hls::stream<w_t8> &fifo_w_in) {
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        {
        }
        for (ap_uint<4> c3 = 0; c3 <= 7; c3 += 1) {
          // array
          // pe
          for (ap_uint<2> c6 = 0; c6 <= 1; c6 += 1)
            for (ap_uint<4> c7 = 0; c7 <= 7; c7 += 1)
              for (ap_uint<3> c8 = 0; c8 <= 2; c8 += 1)
                for (ap_uint<3> c9 = 0; c9 <= 2; c9 += 1) {
                  // latency
                  for (ap_uint<3> c10 = 0; c10 <= 3; c10 += 1) {
                    // latency
                    for (ap_uint<4> c11 = 0; c11 <= 4; c11 += 1) {
                      // latency
                      for (ap_uint<4> c12 = 0; c12 <= 6; c12 += 1) {
                      #pragma HLS PIPELINE II=1
                        w_t8 fifo_data;
                        fifo_data = fifo_w_in.read();
                      }
                    }
                  }
                }
        }
      }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out_intra_trans(int idx, int idy, int c0, int c1, int c2, cout_t2 local_cout[5][14][2], hls::stream<float> &fifo_cout_drain_local_in) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  ap_uint<32> data_split[2];
  #pragma HLS ARRAY_PARTITION variable=data_split complete
  /* Variable Declaration */


  // io_L1
  // pe
  for (ap_uint<2> c6 = 0; c6 <= 1; c6 += 1) {
    // latency
    for (ap_uint<3> c10 = 0; c10 <= 3; c10 += 1) {
      // latency
      for (ap_uint<4> c11 = 0; c11 <= 4; c11 += 1) {
        // latency
        for (ap_uint<4> c12 = 0; c12 <= 6; c12 += 1) {
        #pragma HLS PIPELINE II=1
          // simd
          {
            cout_t1 in_data;
            cout_t2 out_data;
            in_data = fifo_cout_drain_local_in.read();
            int split_idx = (c10) % 2;
            out_data = local_cout[c11][c12 + 7*c6][c10 / 2];
            for (ap_uint<2> n = 0; n < 2; n++) {
            #pragma HLS UNROLL
              data_split[n] = out_data(31, 0);
              out_data = out_data >> 32;
            }
            union {unsigned int ui; float ut;} u;
            u.ut = in_data;
            data_split[split_idx] = ap_uint<32>(u.ui);
            out_data = (data_split[1], data_split[0]);
            local_cout[c11][c12 + 7*c6][c10 / 2] = out_data;
          }
        }
      }
    }
  }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out_inter_trans(int idx, int idy, int c0, int c1, int c2, cout_t2 local_cout[5][14][2], hls::stream<cout_t2> &fifo_cout_drain_in, hls::stream<cout_t2> &fifo_cout_drain_out) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (ap_uint<5> c5 = p1; c5 <= 15; c5 += 1) {
    // io_L1
    if (c5 == p1) {
      for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
        for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
          // access_coalesce
          for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
          #pragma HLS PIPELINE II=1
            {
              cout_t2 in_data;
              cout_t2 out_data;
              in_data = local_cout[c6][c7][c8];
              out_data = in_data;
              fifo_cout_drain_out.write(out_data);
            }
          }
        }
    } else {
      for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
        for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
          // access_coalesce
          for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
          #pragma HLS PIPELINE II=1
            {
              cout_t2 in_data;
              cout_t2 out_data;
              in_data = fifo_cout_drain_in.read();
              out_data = in_data;
              fifo_cout_drain_out.write(out_data);
            }
          }
        }
    }
  }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out_inter_trans_boundary(int idx, int idy, int c0, int c1, int c2, cout_t2 local_cout[5][14][2], hls::stream<cout_t2> &fifo_cout_drain_out) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  /* Variable Declaration */

  for (ap_uint<5> c5 = p1; c5 <= 15; c5 += 1)
    if (c5 == p1) {
      // io_L1
      for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
        for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
          // access_coalesce
          for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
          #pragma HLS PIPELINE II=1
            {
              cout_t2 in_data;
              cout_t2 out_data;
              in_data = local_cout[c6][c7][c8];
              out_data = in_data;
              fifo_cout_drain_out.write(out_data);
            }
          }
        }
    }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out(int idx, int idy, hls::stream<cout_t2> &fifo_cout_drain_in, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<float> &fifo_cout_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  cout_t2 local_cout[5][14][2];
  #pragma HLS RESOURCE variable=local_cout core=RAM_2P_BRAM
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        // io_L2
        cout_drain_IO_L1_out_intra_trans(
          /* module id */ idx, 
          /* module id */ idy, 
          /* host iter */ c0, 
          /* host iter */ c1, 
          /* host iter */ c2, 
          /* array */ local_cout, 
          /* fifo */ fifo_cout_drain_local_in
        );
        cout_drain_IO_L1_out_inter_trans(
          /* module id */ idx, 
          /* module id */ idy, 
          /* host iter */ c0, 
          /* host iter */ c1, 
          /* host iter */ c2, 
          /* array */ local_cout, 
          /* fifo */ fifo_cout_drain_in, 
          /* fifo */ fifo_cout_drain_out
        );
      }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out_wrapper(int idx, int idy, hls::stream<cout_t2> &fifo_cout_drain_in, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<float> &fifo_cout_drain_local_in)
 {
  cout_drain_IO_L1_out(
    /* module id */ idx, 
    /* module id */ idy, 
    /* fifo */ fifo_cout_drain_in, 
    /* fifo */ fifo_cout_drain_out, 
    /* fifo */ fifo_cout_drain_local_in);
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out_boundary(int idx, int idy, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<float> &fifo_cout_drain_local_in) {
#pragma HLS INLINE
  /* Variable Declaration */
  int p0 = idx, p1 = idy; // module id
  cout_t2 local_cout[5][14][2];
  #pragma HLS RESOURCE variable=local_cout core=RAM_2P_BRAM
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        // io_L2
        cout_drain_IO_L1_out_intra_trans(
          /* module id */ idx, 
          /* module id */ idy, 
          /* host iter */ c0, 
          /* host iter */ c1, 
          /* host iter */ c2, 
          /* array */ local_cout, 
          /* fifo */ fifo_cout_drain_local_in
        );
        cout_drain_IO_L1_out_inter_trans_boundary(
          /* module id */ idx, 
          /* module id */ idy, 
          /* host iter */ c0, 
          /* host iter */ c1, 
          /* host iter */ c2, 
          /* array */ local_cout, 
          /* fifo */ fifo_cout_drain_out
        );
      }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L1_out_boundary_wrapper(int idx, int idy, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<float> &fifo_cout_drain_local_in)
 {
  cout_drain_IO_L1_out_boundary(
    /* module id */ idx, 
    /* module id */ idy, 
    /* fifo */ fifo_cout_drain_out, 
    /* fifo */ fifo_cout_drain_local_in);
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L2_out(int idx, hls::stream<cout_t2> &fifo_cout_drain_in, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<cout_t2> &fifo_cout_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (ap_uint<2> c4 = p0; c4 <= 1; c4 += 1) {
          // io_L2
          if (c4 == p0) {
            for (ap_uint<5> c5 = 0; c5 <= 15; c5 += 1) {
              // io_L1
              for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
                for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
                  // access_coalesce
                  for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
                  #pragma HLS PIPELINE II=1
                    {
                      cout_t2 in_data;
                      cout_t2 out_data;
                      in_data = fifo_cout_drain_local_in.read();
                      out_data = in_data;
                      fifo_cout_drain_out.write(out_data);
                    }
                  }
                }
            }
          } else {
            for (ap_uint<5> c5 = 0; c5 <= 15; c5 += 1) {
              // io_L1
              for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
                for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
                  // access_coalesce
                  for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
                  #pragma HLS PIPELINE II=1
                    {
                      cout_t2 in_data;
                      cout_t2 out_data;
                      in_data = fifo_cout_drain_in.read();
                      out_data = in_data;
                      fifo_cout_drain_out.write(out_data);
                    }
                  }
                }
            }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L2_out_boundary(int idx, hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<cout_t2> &fifo_cout_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  int p0 = idx; // module id
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (ap_uint<2> c4 = p0; c4 <= 1; c4 += 1)
          if (c4 == p0) {
            // io_L2
            for (ap_uint<5> c5 = 0; c5 <= 15; c5 += 1) {
              // io_L1
              for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
                for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
                  // access_coalesce
                  for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
                  #pragma HLS PIPELINE II=1
                    {
                      cout_t2 in_data;
                      cout_t2 out_data;
                      in_data = fifo_cout_drain_local_in.read();
                      out_data = in_data;
                      fifo_cout_drain_out.write(out_data);
                    }
                  }
                }
            }
          }
      }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L3_out(hls::stream<cout_t2> &fifo_cout_drain_out, hls::stream<cout_t2> &fifo_cout_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (ap_uint<4> c0 = 0; c0 <= 7; c0 += 1)
    for (ap_uint<4> c1 = 0; c1 <= 5; c1 += 1)
      for (ap_uint<3> c2 = 0; c2 <= 3; c2 += 1) {
        // array
        // io_L3
        for (ap_uint<2> c4 = 0; c4 <= 1; c4 += 1) {
          // io_L2
          for (ap_uint<5> c5 = 0; c5 <= 15; c5 += 1) {
            // io_L1
            for (ap_uint<4> c6 = 0; c6 <= 4; c6 += 1)
              for (ap_uint<5> c7 = 0; c7 <= 13; c7 += 1) {
                // access_coalesce
                // access_serialize
                for (ap_uint<2> c8 = 0; c8 <= 1; c8 += 1) {
                #pragma HLS PIPELINE II=1
                  {
                    cout_t2 in_data;
                    cout_t2 out_data;
                    in_data = fifo_cout_drain_local_in.read();
                    out_data = in_data;
                    fifo_cout_drain_out.write(out_data);
                  }
                }
              }
          }
        }
      }
}
/* Module Definition */

/* Module Definition */
void cout_drain_IO_L3_out_serialize(cout_t16 *cout, hls::stream<cout_t2> &fifo_cout_drain_local_in) {
#pragma HLS INLINE OFF
  /* Variable Declaration */
  /* Variable Declaration */

  for (ap_uint<18> i = 0; i < 107520; i++) {
  #pragma HLS PIPELINE II=1
    cout_t2 fifo_data;
    cout_t16 mem_data;
    cout_t2 mem_data_split[8];
    #pragma HLS ARRAY_PARTITION variable=mem_data_split complete
    for (ap_uint<4> p = 0; p < 8; p++) {
      fifo_data = fifo_cout_drain_local_in.read();
      mem_data_split[p] = fifo_data;
    }
    mem_data = (mem_data_split[7], mem_data_split[6], mem_data_split[5], mem_data_split[4], mem_data_split[3], mem_data_split[2], mem_data_split[1], mem_data_split[0]);
    cout[i] = mem_data;
  }
}
/* Module Definition */

void kernel0(cin_t16 *cin, cout_t16 *cout, w_t16 *w)
{
#pragma HLS INTERFACE m_axi port=cin offset=slave bundle=gmem_cin
#pragma HLS INTERFACE m_axi port=cout offset=slave bundle=gmem_cout
#pragma HLS INTERFACE m_axi port=w offset=slave bundle=gmem_w
#pragma HLS INTERFACE s_axilite port=cin bundle=control
#pragma HLS INTERFACE s_axilite port=cout bundle=control
#pragma HLS INTERFACE s_axilite port=w bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

#pragma HLS DATAFLOW disable_start_propagation

  /* FIFO Declaration */
  /* cin_IO_L3_in_serialize fifo */ hls::stream<cin_t8> fifo_cin_cin_IO_L3_in_serialize;
  #pragma HLS STREAM variable=fifo_cin_cin_IO_L3_in_serialize depth=2
  /* w_IO_L3_in_serialize fifo */ hls::stream<w_t8> fifo_w_w_IO_L3_in_serialize;
  #pragma HLS STREAM variable=fifo_w_w_IO_L3_in_serialize depth=2
  /* cout_drain_IO_L3_out_serialize fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L3_out_serialize;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L3_out_serialize depth=2
  /* cin_IO_L2_in fifo */ hls::stream<cin_t8> fifo_cin_cin_IO_L2_in_0;
  #pragma HLS STREAM variable=fifo_cin_cin_IO_L2_in_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_cin_IO_L2_in_0 core=FIFO_SRL
  /* cin_IO_L2_in fifo */ hls::stream<cin_t8> fifo_cin_cin_IO_L2_in_1;
  #pragma HLS STREAM variable=fifo_cin_cin_IO_L2_in_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_cin_IO_L2_in_1 core=FIFO_SRL
  /* cin_IO_L2_in fifo */ hls::stream<cin_t8> fifo_cin_cin_IO_L2_in_2;
  #pragma HLS STREAM variable=fifo_cin_cin_IO_L2_in_2 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_cin_IO_L2_in_2 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_0;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_0 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_1;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_1 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_2;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_2 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_3;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_3 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_3 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_4;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_4 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_4 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_5;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_5 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_5 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_6;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_6 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_6 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_7;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_7 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_7 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_8;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_8 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_8 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_9;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_9 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_9 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_10;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_10 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_10 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_11;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_11 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_11 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_12;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_12 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_12 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_13;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_13 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_13 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_14;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_14 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_14 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_15;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_15 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_15 core=FIFO_SRL
  /* w_IO_L2_in fifo */ hls::stream<w_t8> fifo_w_w_IO_L2_in_16;
  #pragma HLS STREAM variable=fifo_w_w_IO_L2_in_16 depth=2
  #pragma HLS RESOURCE variable=fifo_w_w_IO_L2_in_16 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_0_0;
  #pragma HLS STREAM variable=fifo_cin_PE_0_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_0_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_1_0;
  #pragma HLS STREAM variable=fifo_cin_PE_1_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_1_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_2_0;
  #pragma HLS STREAM variable=fifo_cin_PE_2_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_2_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_3_0;
  #pragma HLS STREAM variable=fifo_cin_PE_3_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_3_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_4_0;
  #pragma HLS STREAM variable=fifo_cin_PE_4_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_4_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_5_0;
  #pragma HLS STREAM variable=fifo_cin_PE_5_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_5_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_6_0;
  #pragma HLS STREAM variable=fifo_cin_PE_6_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_6_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_7_0;
  #pragma HLS STREAM variable=fifo_cin_PE_7_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_7_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_8_0;
  #pragma HLS STREAM variable=fifo_cin_PE_8_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_8_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_9_0;
  #pragma HLS STREAM variable=fifo_cin_PE_9_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_9_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_10_0;
  #pragma HLS STREAM variable=fifo_cin_PE_10_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_10_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_11_0;
  #pragma HLS STREAM variable=fifo_cin_PE_11_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_11_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_12_0;
  #pragma HLS STREAM variable=fifo_cin_PE_12_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_12_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_13_0;
  #pragma HLS STREAM variable=fifo_cin_PE_13_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_13_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_14_0;
  #pragma HLS STREAM variable=fifo_cin_PE_14_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_14_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_15_0;
  #pragma HLS STREAM variable=fifo_cin_PE_15_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_15_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_16_0;
  #pragma HLS STREAM variable=fifo_cin_PE_16_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_16_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_0_1;
  #pragma HLS STREAM variable=fifo_cin_PE_0_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_0_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_1_1;
  #pragma HLS STREAM variable=fifo_cin_PE_1_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_1_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_2_1;
  #pragma HLS STREAM variable=fifo_cin_PE_2_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_2_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_3_1;
  #pragma HLS STREAM variable=fifo_cin_PE_3_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_3_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_4_1;
  #pragma HLS STREAM variable=fifo_cin_PE_4_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_4_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_5_1;
  #pragma HLS STREAM variable=fifo_cin_PE_5_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_5_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_6_1;
  #pragma HLS STREAM variable=fifo_cin_PE_6_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_6_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_7_1;
  #pragma HLS STREAM variable=fifo_cin_PE_7_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_7_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_8_1;
  #pragma HLS STREAM variable=fifo_cin_PE_8_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_8_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_9_1;
  #pragma HLS STREAM variable=fifo_cin_PE_9_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_9_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_10_1;
  #pragma HLS STREAM variable=fifo_cin_PE_10_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_10_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_11_1;
  #pragma HLS STREAM variable=fifo_cin_PE_11_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_11_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_12_1;
  #pragma HLS STREAM variable=fifo_cin_PE_12_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_12_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_13_1;
  #pragma HLS STREAM variable=fifo_cin_PE_13_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_13_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_14_1;
  #pragma HLS STREAM variable=fifo_cin_PE_14_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_14_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_15_1;
  #pragma HLS STREAM variable=fifo_cin_PE_15_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_15_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<cin_t8> fifo_cin_PE_16_1;
  #pragma HLS STREAM variable=fifo_cin_PE_16_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cin_PE_16_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_0_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_0_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_0_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_1_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_1_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_1_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_2_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_2_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_2_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_3_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_3_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_3_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_4_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_4_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_4_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_5_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_5_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_5_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_6_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_6_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_6_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_7_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_7_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_7_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_8_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_8_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_8_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_9_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_9_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_9_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_10_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_10_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_10_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_11_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_11_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_11_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_12_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_12_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_12_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_13_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_13_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_13_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_14_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_14_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_14_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_15_0;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_15_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_15_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_0_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_0_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_0_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_1_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_1_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_1_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_2_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_2_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_2_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_3_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_3_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_3_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_4_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_4_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_4_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_5_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_5_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_5_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_6_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_6_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_6_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_7_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_7_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_7_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_8_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_8_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_8_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_9_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_9_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_9_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_10_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_10_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_10_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_11_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_11_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_11_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_12_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_12_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_12_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_13_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_13_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_13_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_14_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_14_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_14_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<float> fifo_cout_drain_PE_15_1;
  #pragma HLS STREAM variable=fifo_cout_drain_PE_15_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_PE_15_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_0_0;
  #pragma HLS STREAM variable=fifo_w_PE_0_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_0_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_0_1;
  #pragma HLS STREAM variable=fifo_w_PE_0_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_0_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_0_2;
  #pragma HLS STREAM variable=fifo_w_PE_0_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_0_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_1_0;
  #pragma HLS STREAM variable=fifo_w_PE_1_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_1_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_1_1;
  #pragma HLS STREAM variable=fifo_w_PE_1_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_1_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_1_2;
  #pragma HLS STREAM variable=fifo_w_PE_1_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_1_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_2_0;
  #pragma HLS STREAM variable=fifo_w_PE_2_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_2_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_2_1;
  #pragma HLS STREAM variable=fifo_w_PE_2_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_2_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_2_2;
  #pragma HLS STREAM variable=fifo_w_PE_2_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_2_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_3_0;
  #pragma HLS STREAM variable=fifo_w_PE_3_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_3_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_3_1;
  #pragma HLS STREAM variable=fifo_w_PE_3_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_3_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_3_2;
  #pragma HLS STREAM variable=fifo_w_PE_3_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_3_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_4_0;
  #pragma HLS STREAM variable=fifo_w_PE_4_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_4_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_4_1;
  #pragma HLS STREAM variable=fifo_w_PE_4_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_4_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_4_2;
  #pragma HLS STREAM variable=fifo_w_PE_4_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_4_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_5_0;
  #pragma HLS STREAM variable=fifo_w_PE_5_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_5_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_5_1;
  #pragma HLS STREAM variable=fifo_w_PE_5_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_5_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_5_2;
  #pragma HLS STREAM variable=fifo_w_PE_5_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_5_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_6_0;
  #pragma HLS STREAM variable=fifo_w_PE_6_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_6_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_6_1;
  #pragma HLS STREAM variable=fifo_w_PE_6_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_6_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_6_2;
  #pragma HLS STREAM variable=fifo_w_PE_6_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_6_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_7_0;
  #pragma HLS STREAM variable=fifo_w_PE_7_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_7_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_7_1;
  #pragma HLS STREAM variable=fifo_w_PE_7_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_7_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_7_2;
  #pragma HLS STREAM variable=fifo_w_PE_7_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_7_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_8_0;
  #pragma HLS STREAM variable=fifo_w_PE_8_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_8_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_8_1;
  #pragma HLS STREAM variable=fifo_w_PE_8_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_8_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_8_2;
  #pragma HLS STREAM variable=fifo_w_PE_8_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_8_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_9_0;
  #pragma HLS STREAM variable=fifo_w_PE_9_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_9_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_9_1;
  #pragma HLS STREAM variable=fifo_w_PE_9_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_9_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_9_2;
  #pragma HLS STREAM variable=fifo_w_PE_9_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_9_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_10_0;
  #pragma HLS STREAM variable=fifo_w_PE_10_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_10_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_10_1;
  #pragma HLS STREAM variable=fifo_w_PE_10_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_10_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_10_2;
  #pragma HLS STREAM variable=fifo_w_PE_10_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_10_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_11_0;
  #pragma HLS STREAM variable=fifo_w_PE_11_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_11_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_11_1;
  #pragma HLS STREAM variable=fifo_w_PE_11_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_11_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_11_2;
  #pragma HLS STREAM variable=fifo_w_PE_11_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_11_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_12_0;
  #pragma HLS STREAM variable=fifo_w_PE_12_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_12_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_12_1;
  #pragma HLS STREAM variable=fifo_w_PE_12_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_12_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_12_2;
  #pragma HLS STREAM variable=fifo_w_PE_12_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_12_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_13_0;
  #pragma HLS STREAM variable=fifo_w_PE_13_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_13_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_13_1;
  #pragma HLS STREAM variable=fifo_w_PE_13_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_13_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_13_2;
  #pragma HLS STREAM variable=fifo_w_PE_13_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_13_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_14_0;
  #pragma HLS STREAM variable=fifo_w_PE_14_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_14_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_14_1;
  #pragma HLS STREAM variable=fifo_w_PE_14_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_14_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_14_2;
  #pragma HLS STREAM variable=fifo_w_PE_14_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_14_2 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_15_0;
  #pragma HLS STREAM variable=fifo_w_PE_15_0 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_15_0 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_15_1;
  #pragma HLS STREAM variable=fifo_w_PE_15_1 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_15_1 core=FIFO_SRL
  /* PE fifo */ hls::stream<w_t8> fifo_w_PE_15_2;
  #pragma HLS STREAM variable=fifo_w_PE_15_2 depth=2
  #pragma HLS RESOURCE variable=fifo_w_PE_15_2 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_0;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_0 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_1;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_1 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_2;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_2 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_2 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_3;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_3 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_3 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_4;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_4 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_4 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_5;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_5 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_5 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_6;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_6 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_6 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_7;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_7 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_7 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_8;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_8 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_8 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_9;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_9 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_9 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_10;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_10 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_10 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_11;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_11 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_11 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_12;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_12 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_12 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_13;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_13 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_13 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_14;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_14 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_14 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_15;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_15 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_15 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_0_16;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_0_16 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_0_16 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_0;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_0 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_1;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_1 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_2;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_2 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_2 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_3;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_3 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_3 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_4;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_4 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_4 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_5;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_5 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_5 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_6;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_6 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_6 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_7;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_7 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_7 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_8;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_8 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_8 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_9;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_9 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_9 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_10;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_10 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_10 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_11;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_11 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_11 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_12;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_12 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_12 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_13;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_13 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_13 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_14;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_14 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_14 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_15;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_15 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_15 core=FIFO_SRL
  /* cout_drain_IO_L1_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L1_out_1_16;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L1_out_1_16 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L1_out_1_16 core=FIFO_SRL
  /* cout_drain_IO_L2_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L2_out_0;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L2_out_0 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L2_out_0 core=FIFO_SRL
  /* cout_drain_IO_L2_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L2_out_1;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L2_out_1 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L2_out_1 core=FIFO_SRL
  /* cout_drain_IO_L2_out fifo */ hls::stream<cout_t2> fifo_cout_drain_cout_drain_IO_L2_out_2;
  #pragma HLS STREAM variable=fifo_cout_drain_cout_drain_IO_L2_out_2 depth=2
  #pragma HLS RESOURCE variable=fifo_cout_drain_cout_drain_IO_L2_out_2 core=FIFO_SRL
  /* FIFO Declaration */

  /* Module Call */
  cin_IO_L3_in_serialize(
    /* array */ cin,
    /* fifo */ fifo_cin_cin_IO_L3_in_serialize
  );
  /* Module Call */

  /* Module Call */
  cin_IO_L3_in(
    /* fifo */ fifo_cin_cin_IO_L3_in_serialize,
    /* fifo */ fifo_cin_cin_IO_L2_in_0
  );
  /* Module Call */

  /* Module Call */
  cin_IO_L2_in(
    /* module id */ 0,
    /* fifo */ fifo_cin_cin_IO_L2_in_0,
    /* fifo */ fifo_cin_cin_IO_L2_in_1,
    /* fifo */ fifo_cin_PE_0_0
  );
  /* Module Call */

  /* Module Call */
  cin_IO_L2_in_boundary(
    /* module id */ 1,
    /* fifo */ fifo_cin_cin_IO_L2_in_1,
    /* fifo */ fifo_cin_PE_0_1
  );
  /* Module Call */

  /* Module Call */
  w_IO_L3_in_serialize(
    /* array */ w,
    /* fifo */ fifo_w_w_IO_L3_in_serialize
  );
  /* Module Call */

  /* Module Call */
  w_IO_L3_in(
    /* fifo */ fifo_w_w_IO_L3_in_serialize,
    /* fifo */ fifo_w_w_IO_L2_in_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 0,
    /* fifo */ fifo_w_w_IO_L2_in_0,
    /* fifo */ fifo_w_w_IO_L2_in_1,
    /* fifo */ fifo_w_PE_0_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 1,
    /* fifo */ fifo_w_w_IO_L2_in_1,
    /* fifo */ fifo_w_w_IO_L2_in_2,
    /* fifo */ fifo_w_PE_1_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 2,
    /* fifo */ fifo_w_w_IO_L2_in_2,
    /* fifo */ fifo_w_w_IO_L2_in_3,
    /* fifo */ fifo_w_PE_2_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 3,
    /* fifo */ fifo_w_w_IO_L2_in_3,
    /* fifo */ fifo_w_w_IO_L2_in_4,
    /* fifo */ fifo_w_PE_3_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 4,
    /* fifo */ fifo_w_w_IO_L2_in_4,
    /* fifo */ fifo_w_w_IO_L2_in_5,
    /* fifo */ fifo_w_PE_4_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 5,
    /* fifo */ fifo_w_w_IO_L2_in_5,
    /* fifo */ fifo_w_w_IO_L2_in_6,
    /* fifo */ fifo_w_PE_5_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 6,
    /* fifo */ fifo_w_w_IO_L2_in_6,
    /* fifo */ fifo_w_w_IO_L2_in_7,
    /* fifo */ fifo_w_PE_6_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 7,
    /* fifo */ fifo_w_w_IO_L2_in_7,
    /* fifo */ fifo_w_w_IO_L2_in_8,
    /* fifo */ fifo_w_PE_7_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 8,
    /* fifo */ fifo_w_w_IO_L2_in_8,
    /* fifo */ fifo_w_w_IO_L2_in_9,
    /* fifo */ fifo_w_PE_8_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 9,
    /* fifo */ fifo_w_w_IO_L2_in_9,
    /* fifo */ fifo_w_w_IO_L2_in_10,
    /* fifo */ fifo_w_PE_9_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 10,
    /* fifo */ fifo_w_w_IO_L2_in_10,
    /* fifo */ fifo_w_w_IO_L2_in_11,
    /* fifo */ fifo_w_PE_10_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 11,
    /* fifo */ fifo_w_w_IO_L2_in_11,
    /* fifo */ fifo_w_w_IO_L2_in_12,
    /* fifo */ fifo_w_PE_11_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 12,
    /* fifo */ fifo_w_w_IO_L2_in_12,
    /* fifo */ fifo_w_w_IO_L2_in_13,
    /* fifo */ fifo_w_PE_12_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 13,
    /* fifo */ fifo_w_w_IO_L2_in_13,
    /* fifo */ fifo_w_w_IO_L2_in_14,
    /* fifo */ fifo_w_PE_13_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in(
    /* module id */ 14,
    /* fifo */ fifo_w_w_IO_L2_in_14,
    /* fifo */ fifo_w_w_IO_L2_in_15,
    /* fifo */ fifo_w_PE_14_0
  );
  /* Module Call */

  /* Module Call */
  w_IO_L2_in_boundary(
    /* module id */ 15,
    /* fifo */ fifo_w_w_IO_L2_in_15,
    /* fifo */ fifo_w_PE_15_0
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 0,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_0_0,
    /* fifo */ fifo_cin_PE_1_0,
    /* fifo */ fifo_cout_drain_PE_0_0,
    /* fifo */ fifo_w_PE_0_0,
    /* fifo */ fifo_w_PE_0_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 0,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_0_1,
    /* fifo */ fifo_cin_PE_1_1,
    /* fifo */ fifo_cout_drain_PE_0_1,
    /* fifo */ fifo_w_PE_0_1,
    /* fifo */ fifo_w_PE_0_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 1,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_1_0,
    /* fifo */ fifo_cin_PE_2_0,
    /* fifo */ fifo_cout_drain_PE_1_0,
    /* fifo */ fifo_w_PE_1_0,
    /* fifo */ fifo_w_PE_1_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 1,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_1_1,
    /* fifo */ fifo_cin_PE_2_1,
    /* fifo */ fifo_cout_drain_PE_1_1,
    /* fifo */ fifo_w_PE_1_1,
    /* fifo */ fifo_w_PE_1_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 2,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_2_0,
    /* fifo */ fifo_cin_PE_3_0,
    /* fifo */ fifo_cout_drain_PE_2_0,
    /* fifo */ fifo_w_PE_2_0,
    /* fifo */ fifo_w_PE_2_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 2,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_2_1,
    /* fifo */ fifo_cin_PE_3_1,
    /* fifo */ fifo_cout_drain_PE_2_1,
    /* fifo */ fifo_w_PE_2_1,
    /* fifo */ fifo_w_PE_2_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 3,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_3_0,
    /* fifo */ fifo_cin_PE_4_0,
    /* fifo */ fifo_cout_drain_PE_3_0,
    /* fifo */ fifo_w_PE_3_0,
    /* fifo */ fifo_w_PE_3_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 3,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_3_1,
    /* fifo */ fifo_cin_PE_4_1,
    /* fifo */ fifo_cout_drain_PE_3_1,
    /* fifo */ fifo_w_PE_3_1,
    /* fifo */ fifo_w_PE_3_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 4,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_4_0,
    /* fifo */ fifo_cin_PE_5_0,
    /* fifo */ fifo_cout_drain_PE_4_0,
    /* fifo */ fifo_w_PE_4_0,
    /* fifo */ fifo_w_PE_4_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 4,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_4_1,
    /* fifo */ fifo_cin_PE_5_1,
    /* fifo */ fifo_cout_drain_PE_4_1,
    /* fifo */ fifo_w_PE_4_1,
    /* fifo */ fifo_w_PE_4_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 5,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_5_0,
    /* fifo */ fifo_cin_PE_6_0,
    /* fifo */ fifo_cout_drain_PE_5_0,
    /* fifo */ fifo_w_PE_5_0,
    /* fifo */ fifo_w_PE_5_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 5,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_5_1,
    /* fifo */ fifo_cin_PE_6_1,
    /* fifo */ fifo_cout_drain_PE_5_1,
    /* fifo */ fifo_w_PE_5_1,
    /* fifo */ fifo_w_PE_5_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 6,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_6_0,
    /* fifo */ fifo_cin_PE_7_0,
    /* fifo */ fifo_cout_drain_PE_6_0,
    /* fifo */ fifo_w_PE_6_0,
    /* fifo */ fifo_w_PE_6_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 6,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_6_1,
    /* fifo */ fifo_cin_PE_7_1,
    /* fifo */ fifo_cout_drain_PE_6_1,
    /* fifo */ fifo_w_PE_6_1,
    /* fifo */ fifo_w_PE_6_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 7,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_7_0,
    /* fifo */ fifo_cin_PE_8_0,
    /* fifo */ fifo_cout_drain_PE_7_0,
    /* fifo */ fifo_w_PE_7_0,
    /* fifo */ fifo_w_PE_7_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 7,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_7_1,
    /* fifo */ fifo_cin_PE_8_1,
    /* fifo */ fifo_cout_drain_PE_7_1,
    /* fifo */ fifo_w_PE_7_1,
    /* fifo */ fifo_w_PE_7_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 8,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_8_0,
    /* fifo */ fifo_cin_PE_9_0,
    /* fifo */ fifo_cout_drain_PE_8_0,
    /* fifo */ fifo_w_PE_8_0,
    /* fifo */ fifo_w_PE_8_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 8,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_8_1,
    /* fifo */ fifo_cin_PE_9_1,
    /* fifo */ fifo_cout_drain_PE_8_1,
    /* fifo */ fifo_w_PE_8_1,
    /* fifo */ fifo_w_PE_8_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 9,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_9_0,
    /* fifo */ fifo_cin_PE_10_0,
    /* fifo */ fifo_cout_drain_PE_9_0,
    /* fifo */ fifo_w_PE_9_0,
    /* fifo */ fifo_w_PE_9_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 9,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_9_1,
    /* fifo */ fifo_cin_PE_10_1,
    /* fifo */ fifo_cout_drain_PE_9_1,
    /* fifo */ fifo_w_PE_9_1,
    /* fifo */ fifo_w_PE_9_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 10,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_10_0,
    /* fifo */ fifo_cin_PE_11_0,
    /* fifo */ fifo_cout_drain_PE_10_0,
    /* fifo */ fifo_w_PE_10_0,
    /* fifo */ fifo_w_PE_10_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 10,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_10_1,
    /* fifo */ fifo_cin_PE_11_1,
    /* fifo */ fifo_cout_drain_PE_10_1,
    /* fifo */ fifo_w_PE_10_1,
    /* fifo */ fifo_w_PE_10_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 11,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_11_0,
    /* fifo */ fifo_cin_PE_12_0,
    /* fifo */ fifo_cout_drain_PE_11_0,
    /* fifo */ fifo_w_PE_11_0,
    /* fifo */ fifo_w_PE_11_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 11,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_11_1,
    /* fifo */ fifo_cin_PE_12_1,
    /* fifo */ fifo_cout_drain_PE_11_1,
    /* fifo */ fifo_w_PE_11_1,
    /* fifo */ fifo_w_PE_11_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 12,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_12_0,
    /* fifo */ fifo_cin_PE_13_0,
    /* fifo */ fifo_cout_drain_PE_12_0,
    /* fifo */ fifo_w_PE_12_0,
    /* fifo */ fifo_w_PE_12_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 12,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_12_1,
    /* fifo */ fifo_cin_PE_13_1,
    /* fifo */ fifo_cout_drain_PE_12_1,
    /* fifo */ fifo_w_PE_12_1,
    /* fifo */ fifo_w_PE_12_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 13,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_13_0,
    /* fifo */ fifo_cin_PE_14_0,
    /* fifo */ fifo_cout_drain_PE_13_0,
    /* fifo */ fifo_w_PE_13_0,
    /* fifo */ fifo_w_PE_13_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 13,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_13_1,
    /* fifo */ fifo_cin_PE_14_1,
    /* fifo */ fifo_cout_drain_PE_13_1,
    /* fifo */ fifo_w_PE_13_1,
    /* fifo */ fifo_w_PE_13_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 14,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_14_0,
    /* fifo */ fifo_cin_PE_15_0,
    /* fifo */ fifo_cout_drain_PE_14_0,
    /* fifo */ fifo_w_PE_14_0,
    /* fifo */ fifo_w_PE_14_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 14,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_14_1,
    /* fifo */ fifo_cin_PE_15_1,
    /* fifo */ fifo_cout_drain_PE_14_1,
    /* fifo */ fifo_w_PE_14_1,
    /* fifo */ fifo_w_PE_14_2
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 15,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_15_0,
    /* fifo */ fifo_cin_PE_16_0,
    /* fifo */ fifo_cout_drain_PE_15_0,
    /* fifo */ fifo_w_PE_15_0,
    /* fifo */ fifo_w_PE_15_1
  );
  /* Module Call */

  /* Module Call */
  PE_wrapper(
    /* module id */ 15,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_15_1,
    /* fifo */ fifo_cin_PE_16_1,
    /* fifo */ fifo_cout_drain_PE_15_1,
    /* fifo */ fifo_w_PE_15_1,
    /* fifo */ fifo_w_PE_15_2
  );
  /* Module Call */

  /* Module Call */
  cin_PE_dummy_in(
    /* module id */ 15,
    /* module id */ 0,
    /* fifo */ fifo_cin_PE_16_0
  );
  /* Module Call */

  /* Module Call */
  cin_PE_dummy_in(
    /* module id */ 15,
    /* module id */ 1,
    /* fifo */ fifo_cin_PE_16_1
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 0,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_0_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 1,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_1_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 2,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_2_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 3,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_3_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 4,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_4_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 5,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_5_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 6,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_6_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 7,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_7_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 8,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_8_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 9,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_9_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 10,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_10_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 11,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_11_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 12,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_12_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 13,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_13_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 14,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_14_2
  );
  /* Module Call */

  /* Module Call */
  w_PE_dummy_in(
    /* module id */ 15,
    /* module id */ 1,
    /* fifo */ fifo_w_PE_15_2
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_boundary_wrapper(
    /* module id */ 0,
    /* module id */ 15,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_15,
    /* fifo */ fifo_cout_drain_PE_15_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 14,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_15,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_14,
    /* fifo */ fifo_cout_drain_PE_14_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 13,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_14,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_13,
    /* fifo */ fifo_cout_drain_PE_13_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 12,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_13,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_12,
    /* fifo */ fifo_cout_drain_PE_12_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 11,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_12,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_11,
    /* fifo */ fifo_cout_drain_PE_11_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 10,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_11,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_10,
    /* fifo */ fifo_cout_drain_PE_10_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 9,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_10,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_9,
    /* fifo */ fifo_cout_drain_PE_9_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 8,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_9,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_8,
    /* fifo */ fifo_cout_drain_PE_8_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 7,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_8,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_7,
    /* fifo */ fifo_cout_drain_PE_7_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 6,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_7,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_6,
    /* fifo */ fifo_cout_drain_PE_6_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 5,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_6,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_5,
    /* fifo */ fifo_cout_drain_PE_5_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 4,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_5,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_4,
    /* fifo */ fifo_cout_drain_PE_4_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 3,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_4,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_3,
    /* fifo */ fifo_cout_drain_PE_3_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 2,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_3,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_2,
    /* fifo */ fifo_cout_drain_PE_2_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_2,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_1,
    /* fifo */ fifo_cout_drain_PE_1_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 0,
    /* module id */ 0,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_0,
    /* fifo */ fifo_cout_drain_PE_0_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_boundary_wrapper(
    /* module id */ 1,
    /* module id */ 15,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_15,
    /* fifo */ fifo_cout_drain_PE_15_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 14,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_15,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_14,
    /* fifo */ fifo_cout_drain_PE_14_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 13,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_14,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_13,
    /* fifo */ fifo_cout_drain_PE_13_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 12,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_13,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_12,
    /* fifo */ fifo_cout_drain_PE_12_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 11,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_12,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_11,
    /* fifo */ fifo_cout_drain_PE_11_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 10,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_11,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_10,
    /* fifo */ fifo_cout_drain_PE_10_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 9,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_10,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_9,
    /* fifo */ fifo_cout_drain_PE_9_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 8,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_9,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_8,
    /* fifo */ fifo_cout_drain_PE_8_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 7,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_8,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_7,
    /* fifo */ fifo_cout_drain_PE_7_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 6,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_7,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_6,
    /* fifo */ fifo_cout_drain_PE_6_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 5,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_6,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_5,
    /* fifo */ fifo_cout_drain_PE_5_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 4,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_5,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_4,
    /* fifo */ fifo_cout_drain_PE_4_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 3,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_4,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_3,
    /* fifo */ fifo_cout_drain_PE_3_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 2,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_3,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_2,
    /* fifo */ fifo_cout_drain_PE_2_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_2,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_1,
    /* fifo */ fifo_cout_drain_PE_1_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L1_out_wrapper(
    /* module id */ 1,
    /* module id */ 0,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_0,
    /* fifo */ fifo_cout_drain_PE_0_1
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L2_out_boundary(
    /* module id */ 1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L2_out_1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_1_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L2_out(
    /* module id */ 0,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L2_out_1,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L2_out_0,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L1_out_0_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L3_out(
    /* fifo */ fifo_cout_drain_cout_drain_IO_L3_out_serialize,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L2_out_0
  );
  /* Module Call */

  /* Module Call */
  cout_drain_IO_L3_out_serialize(
    /* array */ cout,
    /* fifo */ fifo_cout_drain_cout_drain_IO_L3_out_serialize
  );
  /* Module Call */

}
