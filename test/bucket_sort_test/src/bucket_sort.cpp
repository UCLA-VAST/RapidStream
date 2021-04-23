#include <stdio.h>
//#include <hls_stream.h>
#include "constant.h"

template<class T>
T HLS_REG(T in){
#pragma HLS pipeline
#pragma HLS inline off
#pragma HLS interface port=return register
    return in;
}


void read_engine (
    bus_t *src,
    hls::stream<bus_t> &dst,
    int line_num
) {
    for (int i = 0; i < line_num; i++) {
#pragma HLS pipeline II=1
        bus_t temp = src[i];
        bus_t temp_delayed = HLS_REG(HLS_REG(temp));
        dst.write(temp_delayed);
    }
}


void write_engine (
    hls::stream<bus_t> &src,
    bus_t *dst
) {
    uint1 end = 0;
    int offset = 0;
    while (end == 0) {
#pragma HLS pipeline II=1
        bus_t temp;
        if (src.read_nb(temp)) {
            if (temp(63, 0) != 0) {
                dst[offset] = temp;
                offset++;
            }
            else {
                end = 1;
            }
        } 
    }
}

extern "C" {
void bucket_sort(
    bus_t *in0,
    bus_t *in1,
    bus_t *in2,
    bus_t *in3,
    bus_t *in4,
    bus_t *in5,
    bus_t *in6,
    bus_t *in7,
    bus_t *out0,
    bus_t *out1,
    bus_t *out2,
    bus_t *out3,
    bus_t *out4,
    bus_t *out5,
    bus_t *out6,
    bus_t *out7,
    int data_size
) {

#pragma HLS INTERFACE m_axi port = in0 offset = slave bundle = hbm0   depth=8192
#pragma HLS INTERFACE m_axi port = in1 offset = slave bundle = hbm2   depth=8192
#pragma HLS INTERFACE m_axi port = in2 offset = slave bundle = hbm4   depth=8192
#pragma HLS INTERFACE m_axi port = in3 offset = slave bundle = hbm6   depth=8192
#pragma HLS INTERFACE m_axi port = in4 offset = slave bundle = hbm8   depth=8192
#pragma HLS INTERFACE m_axi port = in5 offset = slave bundle = hbm10  depth=8192
#pragma HLS INTERFACE m_axi port = in6 offset = slave bundle = hbm12  depth=8192
#pragma HLS INTERFACE m_axi port = in7 offset = slave bundle = hbm14  depth=8192
#pragma HLS INTERFACE m_axi port = out0 offset = slave bundle = hbm16  depth=8192
#pragma HLS INTERFACE m_axi port = out1 offset = slave bundle = hbm18  depth=8192
#pragma HLS INTERFACE m_axi port = out2 offset = slave bundle = hbm20  depth=8192
#pragma HLS INTERFACE m_axi port = out3 offset = slave bundle = hbm22  depth=8192
#pragma HLS INTERFACE m_axi port = out4 offset = slave bundle = hbm23  depth=8192
#pragma HLS INTERFACE m_axi port = out5 offset = slave bundle = hbm24 depth=8192
#pragma HLS INTERFACE m_axi port = out6 offset = slave bundle = hbm25 depth=8192
#pragma HLS INTERFACE m_axi port = out7 offset = slave bundle = hbm26 depth=8192

#pragma HLS INTERFACE s_axilite port = in0 bundle = control
#pragma HLS INTERFACE s_axilite port = in1 bundle = control
#pragma HLS INTERFACE s_axilite port = in2 bundle = control
#pragma HLS INTERFACE s_axilite port = in3 bundle = control
#pragma HLS INTERFACE s_axilite port = in4 bundle = control
#pragma HLS INTERFACE s_axilite port = in5 bundle = control
#pragma HLS INTERFACE s_axilite port = in6 bundle = control
#pragma HLS INTERFACE s_axilite port = in7 bundle = control
#pragma HLS INTERFACE s_axilite port = out0 bundle = control
#pragma HLS INTERFACE s_axilite port = out1 bundle = control
#pragma HLS INTERFACE s_axilite port = out2 bundle = control
#pragma HLS INTERFACE s_axilite port = out3 bundle = control
#pragma HLS INTERFACE s_axilite port = out4 bundle = control
#pragma HLS INTERFACE s_axilite port = out5 bundle = control
#pragma HLS INTERFACE s_axilite port = out6 bundle = control
#pragma HLS INTERFACE s_axilite port = out7 bundle = control


#pragma HLS INTERFACE s_axilite port = data_size bundle = control
#pragma HLS INTERFACE s_axilite port = return bundle = control

#pragma HLS dataflow disable_start_propagation

    // fifos to store input from off-chip memory 
    hls::stream<bus_t> in_fifo_0;
    hls::stream<bus_t> in_fifo_1;
    hls::stream<bus_t> in_fifo_2;
    hls::stream<bus_t> in_fifo_3;
    hls::stream<bus_t> in_fifo_4;
    hls::stream<bus_t> in_fifo_5;
    hls::stream<bus_t> in_fifo_6;
    hls::stream<bus_t> in_fifo_7;

#pragma HLS STREAM variable=in_fifo_0 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_1 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_2 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_3 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_4 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_5 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_6 depth=4 dim=1
#pragma HLS STREAM variable=in_fifo_7 depth=4 dim=1

    // part 2-1: fifos to store output of bitonic sorter
    hls::stream<bus_t> bitonic_fifo_0;
    hls::stream<bus_t> bitonic_fifo_1;
    hls::stream<bus_t> bitonic_fifo_2;
    hls::stream<bus_t> bitonic_fifo_3;
    hls::stream<bus_t> bitonic_fifo_4;
    hls::stream<bus_t> bitonic_fifo_5;
    hls::stream<bus_t> bitonic_fifo_6;
    hls::stream<bus_t> bitonic_fifo_7;

#pragma HLS STREAM variable=bitonic_fifo_0 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_1 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_2 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_3 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_4 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_5 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_6 depth=4 dim=1
#pragma HLS STREAM variable=bitonic_fifo_7 depth=4 dim=1

    // part 2-2: fifos to store output of local frequency counter
    hls::stream<count_t> freq_count_fifo_0;
    hls::stream<count_t> freq_count_fifo_1;
    hls::stream<count_t> freq_count_fifo_2;
    hls::stream<count_t> freq_count_fifo_3;
    hls::stream<count_t> freq_count_fifo_4;
    hls::stream<count_t> freq_count_fifo_5;
    hls::stream<count_t> freq_count_fifo_6;
    hls::stream<count_t> freq_count_fifo_7;

#pragma HLS STREAM variable=freq_count_fifo_0 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_1 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_2 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_3 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_4 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_5 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_6 depth=4 dim=1
#pragma HLS STREAM variable=freq_count_fifo_7 depth=4 dim=1

    // phase 3: fifos to store local shift results
    hls::stream<bus_t> local_shift_data_0_0;
    hls::stream<bus_t> local_shift_data_0_1;
    hls::stream<bus_t> local_shift_data_0_2;
    hls::stream<bus_t> local_shift_data_0_3;
    hls::stream<bus_t> local_shift_data_0_4;
    hls::stream<bus_t> local_shift_data_0_5;
    hls::stream<bus_t> local_shift_data_0_6;
    hls::stream<bus_t> local_shift_data_0_7;
    hls::stream<bus_t> local_shift_data_1_0;
    hls::stream<bus_t> local_shift_data_1_1;
    hls::stream<bus_t> local_shift_data_1_2;
    hls::stream<bus_t> local_shift_data_1_3;
    hls::stream<bus_t> local_shift_data_1_4;
    hls::stream<bus_t> local_shift_data_1_5;
    hls::stream<bus_t> local_shift_data_1_6;
    hls::stream<bus_t> local_shift_data_1_7;
    hls::stream<bus_t> local_shift_data_2_0;
    hls::stream<bus_t> local_shift_data_2_1;
    hls::stream<bus_t> local_shift_data_2_2;
    hls::stream<bus_t> local_shift_data_2_3;
    hls::stream<bus_t> local_shift_data_2_4;
    hls::stream<bus_t> local_shift_data_2_5;
    hls::stream<bus_t> local_shift_data_2_6;
    hls::stream<bus_t> local_shift_data_2_7;
    hls::stream<bus_t> local_shift_data_3_0;
    hls::stream<bus_t> local_shift_data_3_1;
    hls::stream<bus_t> local_shift_data_3_2;
    hls::stream<bus_t> local_shift_data_3_3;
    hls::stream<bus_t> local_shift_data_3_4;
    hls::stream<bus_t> local_shift_data_3_5;
    hls::stream<bus_t> local_shift_data_3_6;
    hls::stream<bus_t> local_shift_data_3_7;
    hls::stream<bus_t> local_shift_data_4_0;
    hls::stream<bus_t> local_shift_data_4_1;
    hls::stream<bus_t> local_shift_data_4_2;
    hls::stream<bus_t> local_shift_data_4_3;
    hls::stream<bus_t> local_shift_data_4_4;
    hls::stream<bus_t> local_shift_data_4_5;
    hls::stream<bus_t> local_shift_data_4_6;
    hls::stream<bus_t> local_shift_data_4_7;
    hls::stream<bus_t> local_shift_data_5_0;
    hls::stream<bus_t> local_shift_data_5_1;
    hls::stream<bus_t> local_shift_data_5_2;
    hls::stream<bus_t> local_shift_data_5_3;
    hls::stream<bus_t> local_shift_data_5_4;
    hls::stream<bus_t> local_shift_data_5_5;
    hls::stream<bus_t> local_shift_data_5_6;
    hls::stream<bus_t> local_shift_data_5_7;
    hls::stream<bus_t> local_shift_data_6_0;
    hls::stream<bus_t> local_shift_data_6_1;
    hls::stream<bus_t> local_shift_data_6_2;
    hls::stream<bus_t> local_shift_data_6_3;
    hls::stream<bus_t> local_shift_data_6_4;
    hls::stream<bus_t> local_shift_data_6_5;
    hls::stream<bus_t> local_shift_data_6_6;
    hls::stream<bus_t> local_shift_data_6_7;
    hls::stream<bus_t> local_shift_data_7_0;
    hls::stream<bus_t> local_shift_data_7_1;
    hls::stream<bus_t> local_shift_data_7_2;
    hls::stream<bus_t> local_shift_data_7_3;
    hls::stream<bus_t> local_shift_data_7_4;
    hls::stream<bus_t> local_shift_data_7_5;
    hls::stream<bus_t> local_shift_data_7_6;
    hls::stream<bus_t> local_shift_data_7_7;
#pragma HLS STREAM variable=local_shift_data_0_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_0_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_1_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_2_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_3_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_4_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_5_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_6_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_data_7_7 depth=2 dim=1

    hls::stream<uint8> local_shift_len_0_0;
    hls::stream<uint8> local_shift_len_0_1;
    hls::stream<uint8> local_shift_len_0_2;
    hls::stream<uint8> local_shift_len_0_3;
    hls::stream<uint8> local_shift_len_0_4;
    hls::stream<uint8> local_shift_len_0_5;
    hls::stream<uint8> local_shift_len_0_6;
    hls::stream<uint8> local_shift_len_0_7;
    hls::stream<uint8> local_shift_len_1_0;
    hls::stream<uint8> local_shift_len_1_1;
    hls::stream<uint8> local_shift_len_1_2;
    hls::stream<uint8> local_shift_len_1_3;
    hls::stream<uint8> local_shift_len_1_4;
    hls::stream<uint8> local_shift_len_1_5;
    hls::stream<uint8> local_shift_len_1_6;
    hls::stream<uint8> local_shift_len_1_7;
    hls::stream<uint8> local_shift_len_2_0;
    hls::stream<uint8> local_shift_len_2_1;
    hls::stream<uint8> local_shift_len_2_2;
    hls::stream<uint8> local_shift_len_2_3;
    hls::stream<uint8> local_shift_len_2_4;
    hls::stream<uint8> local_shift_len_2_5;
    hls::stream<uint8> local_shift_len_2_6;
    hls::stream<uint8> local_shift_len_2_7;
    hls::stream<uint8> local_shift_len_3_0;
    hls::stream<uint8> local_shift_len_3_1;
    hls::stream<uint8> local_shift_len_3_2;
    hls::stream<uint8> local_shift_len_3_3;
    hls::stream<uint8> local_shift_len_3_4;
    hls::stream<uint8> local_shift_len_3_5;
    hls::stream<uint8> local_shift_len_3_6;
    hls::stream<uint8> local_shift_len_3_7;
    hls::stream<uint8> local_shift_len_4_0;
    hls::stream<uint8> local_shift_len_4_1;
    hls::stream<uint8> local_shift_len_4_2;
    hls::stream<uint8> local_shift_len_4_3;
    hls::stream<uint8> local_shift_len_4_4;
    hls::stream<uint8> local_shift_len_4_5;
    hls::stream<uint8> local_shift_len_4_6;
    hls::stream<uint8> local_shift_len_4_7;
    hls::stream<uint8> local_shift_len_5_0;
    hls::stream<uint8> local_shift_len_5_1;
    hls::stream<uint8> local_shift_len_5_2;
    hls::stream<uint8> local_shift_len_5_3;
    hls::stream<uint8> local_shift_len_5_4;
    hls::stream<uint8> local_shift_len_5_5;
    hls::stream<uint8> local_shift_len_5_6;
    hls::stream<uint8> local_shift_len_5_7;
    hls::stream<uint8> local_shift_len_6_0;
    hls::stream<uint8> local_shift_len_6_1;
    hls::stream<uint8> local_shift_len_6_2;
    hls::stream<uint8> local_shift_len_6_3;
    hls::stream<uint8> local_shift_len_6_4;
    hls::stream<uint8> local_shift_len_6_5;
    hls::stream<uint8> local_shift_len_6_6;
    hls::stream<uint8> local_shift_len_6_7;
    hls::stream<uint8> local_shift_len_7_0;
    hls::stream<uint8> local_shift_len_7_1;
    hls::stream<uint8> local_shift_len_7_2;
    hls::stream<uint8> local_shift_len_7_3;
    hls::stream<uint8> local_shift_len_7_4;
    hls::stream<uint8> local_shift_len_7_5;
    hls::stream<uint8> local_shift_len_7_6;
    hls::stream<uint8> local_shift_len_7_7;
#pragma HLS STREAM variable=local_shift_len_0_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_0_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_1_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_2_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_3_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_4_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_5_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_6_7 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_0 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_1 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_2 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_3 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_4 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_5 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_6 depth=2 dim=1
#pragma HLS STREAM variable=local_shift_len_7_7 depth=2 dim=1

    // phase 4: local group
    hls::stream<bus_t> local_group_0_0;
    hls::stream<bus_t> local_group_0_1;
    hls::stream<bus_t> local_group_0_2;
    hls::stream<bus_t> local_group_0_3;
    hls::stream<bus_t> local_group_0_4;
    hls::stream<bus_t> local_group_0_5;
    hls::stream<bus_t> local_group_0_6;
    hls::stream<bus_t> local_group_0_7;
    hls::stream<bus_t> local_group_1_0;
    hls::stream<bus_t> local_group_1_1;
    hls::stream<bus_t> local_group_1_2;
    hls::stream<bus_t> local_group_1_3;
    hls::stream<bus_t> local_group_1_4;
    hls::stream<bus_t> local_group_1_5;
    hls::stream<bus_t> local_group_1_6;
    hls::stream<bus_t> local_group_1_7;
    hls::stream<bus_t> local_group_2_0;
    hls::stream<bus_t> local_group_2_1;
    hls::stream<bus_t> local_group_2_2;
    hls::stream<bus_t> local_group_2_3;
    hls::stream<bus_t> local_group_2_4;
    hls::stream<bus_t> local_group_2_5;
    hls::stream<bus_t> local_group_2_6;
    hls::stream<bus_t> local_group_2_7;
    hls::stream<bus_t> local_group_3_0;
    hls::stream<bus_t> local_group_3_1;
    hls::stream<bus_t> local_group_3_2;
    hls::stream<bus_t> local_group_3_3;
    hls::stream<bus_t> local_group_3_4;
    hls::stream<bus_t> local_group_3_5;
    hls::stream<bus_t> local_group_3_6;
    hls::stream<bus_t> local_group_3_7;
    hls::stream<bus_t> local_group_4_0;
    hls::stream<bus_t> local_group_4_1;
    hls::stream<bus_t> local_group_4_2;
    hls::stream<bus_t> local_group_4_3;
    hls::stream<bus_t> local_group_4_4;
    hls::stream<bus_t> local_group_4_5;
    hls::stream<bus_t> local_group_4_6;
    hls::stream<bus_t> local_group_4_7;
    hls::stream<bus_t> local_group_5_0;
    hls::stream<bus_t> local_group_5_1;
    hls::stream<bus_t> local_group_5_2;
    hls::stream<bus_t> local_group_5_3;
    hls::stream<bus_t> local_group_5_4;
    hls::stream<bus_t> local_group_5_5;
    hls::stream<bus_t> local_group_5_6;
    hls::stream<bus_t> local_group_5_7;
    hls::stream<bus_t> local_group_6_0;
    hls::stream<bus_t> local_group_6_1;
    hls::stream<bus_t> local_group_6_2;
    hls::stream<bus_t> local_group_6_3;
    hls::stream<bus_t> local_group_6_4;
    hls::stream<bus_t> local_group_6_5;
    hls::stream<bus_t> local_group_6_6;
    hls::stream<bus_t> local_group_6_7;
    hls::stream<bus_t> local_group_7_0;
    hls::stream<bus_t> local_group_7_1;
    hls::stream<bus_t> local_group_7_2;
    hls::stream<bus_t> local_group_7_3;
    hls::stream<bus_t> local_group_7_4;
    hls::stream<bus_t> local_group_7_5;
    hls::stream<bus_t> local_group_7_6;
    hls::stream<bus_t> local_group_7_7;
#pragma HLS STREAM variable=local_group_0_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_0_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_1_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_2_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_3_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_4_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_5_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_6_7 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_0 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_1 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_2 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_3 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_4 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_5 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_6 depth=32 dim=1
#pragma HLS STREAM variable=local_group_7_7 depth=32 dim=1

    // phase 5: concatenate
    // fifos to store output to off-chip memory
    hls::stream<bus_t> out_fifo_0;
    hls::stream<bus_t> out_fifo_1;
    hls::stream<bus_t> out_fifo_2;
    hls::stream<bus_t> out_fifo_3;
    hls::stream<bus_t> out_fifo_4;
    hls::stream<bus_t> out_fifo_5;
    hls::stream<bus_t> out_fifo_6;
    hls::stream<bus_t> out_fifo_7;
#pragma HLS STREAM variable=out_fifo_0 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_1 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_2 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_3 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_4 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_5 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_6 depth=4 dim=1
#pragma HLS STREAM variable=out_fifo_7 depth=4 dim=1


int line_num = DIV_CEIL(data_size, RECORD_NUM);

    // phase 1: read data from off-chip memory 
    read_engine (in0, in_fifo_0, line_num);
    read_engine (in1, in_fifo_1, line_num);
    read_engine (in2, in_fifo_2, line_num);
    read_engine (in3, in_fifo_3, line_num);
    read_engine (in4, in_fifo_4, line_num);
    read_engine (in5, in_fifo_5, line_num);
    read_engine (in6, in_fifo_6, line_num);
    read_engine (in7, in_fifo_7, line_num);

    // phase 2: part 2-1 & part 2-2 are in parallel
    bitonic_sort (in_fifo_0, bitonic_fifo_0, freq_count_fifo_0, line_num);
    bitonic_sort (in_fifo_1, bitonic_fifo_1, freq_count_fifo_1, line_num);
    bitonic_sort (in_fifo_2, bitonic_fifo_2, freq_count_fifo_2, line_num);
    bitonic_sort (in_fifo_3, bitonic_fifo_3, freq_count_fifo_3, line_num);
    bitonic_sort (in_fifo_4, bitonic_fifo_4, freq_count_fifo_4, line_num);
    bitonic_sort (in_fifo_5, bitonic_fifo_5, freq_count_fifo_5, line_num);
    bitonic_sort (in_fifo_6, bitonic_fifo_6, freq_count_fifo_6, line_num);
    bitonic_sort (in_fifo_7, bitonic_fifo_7, freq_count_fifo_7, line_num);

    
    // phase 3: local shift
    local_shift (line_num, bitonic_fifo_0, freq_count_fifo_0, 
                local_shift_data_0_0, local_shift_data_0_1, local_shift_data_0_2, local_shift_data_0_3, 
                local_shift_data_0_4, local_shift_data_0_5, local_shift_data_0_6, local_shift_data_0_7, 
                local_shift_len_0_0, local_shift_len_0_1, local_shift_len_0_2, local_shift_len_0_3, 
                local_shift_len_0_4, local_shift_len_0_5, local_shift_len_0_6, local_shift_len_0_7);

    local_shift (line_num, bitonic_fifo_1, freq_count_fifo_1, 
                local_shift_data_1_0, local_shift_data_1_1, local_shift_data_1_2, local_shift_data_1_3, 
                local_shift_data_1_4, local_shift_data_1_5, local_shift_data_1_6, local_shift_data_1_7, 
                local_shift_len_1_0, local_shift_len_1_1, local_shift_len_1_2, local_shift_len_1_3, 
                local_shift_len_1_4, local_shift_len_1_5, local_shift_len_1_6, local_shift_len_1_7);

    local_shift (line_num, bitonic_fifo_2, freq_count_fifo_2, 
                local_shift_data_2_0, local_shift_data_2_1, local_shift_data_2_2, local_shift_data_2_3, 
                local_shift_data_2_4, local_shift_data_2_5, local_shift_data_2_6, local_shift_data_2_7, 
                local_shift_len_2_0, local_shift_len_2_1, local_shift_len_2_2, local_shift_len_2_3, 
                local_shift_len_2_4, local_shift_len_2_5, local_shift_len_2_6, local_shift_len_2_7);

    local_shift (line_num, bitonic_fifo_3, freq_count_fifo_3, 
                local_shift_data_3_0, local_shift_data_3_1, local_shift_data_3_2, local_shift_data_3_3, 
                local_shift_data_3_4, local_shift_data_3_5, local_shift_data_3_6, local_shift_data_3_7, 
                local_shift_len_3_0, local_shift_len_3_1, local_shift_len_3_2, local_shift_len_3_3, 
                local_shift_len_3_4, local_shift_len_3_5, local_shift_len_3_6, local_shift_len_3_7);

    local_shift (line_num, bitonic_fifo_4, freq_count_fifo_4, 
                local_shift_data_4_0, local_shift_data_4_1, local_shift_data_4_2, local_shift_data_4_3, 
                local_shift_data_4_4, local_shift_data_4_5, local_shift_data_4_6, local_shift_data_4_7, 
                local_shift_len_4_0, local_shift_len_4_1, local_shift_len_4_2, local_shift_len_4_3, 
                local_shift_len_4_4, local_shift_len_4_5, local_shift_len_4_6, local_shift_len_4_7);

    local_shift (line_num, bitonic_fifo_5, freq_count_fifo_5, 
                local_shift_data_5_0, local_shift_data_5_1, local_shift_data_5_2, local_shift_data_5_3, 
                local_shift_data_5_4, local_shift_data_5_5, local_shift_data_5_6, local_shift_data_5_7, 
                local_shift_len_5_0, local_shift_len_5_1, local_shift_len_5_2, local_shift_len_5_3, 
                local_shift_len_5_4, local_shift_len_5_5, local_shift_len_5_6, local_shift_len_5_7);

    local_shift (line_num, bitonic_fifo_6, freq_count_fifo_6, 
                local_shift_data_6_0, local_shift_data_6_1, local_shift_data_6_2, local_shift_data_6_3, 
                local_shift_data_6_4, local_shift_data_6_5, local_shift_data_6_6, local_shift_data_6_7, 
                local_shift_len_6_0, local_shift_len_6_1, local_shift_len_6_2, local_shift_len_6_3, 
                local_shift_len_6_4, local_shift_len_6_5, local_shift_len_6_6, local_shift_len_6_7);

    local_shift (line_num, bitonic_fifo_7, freq_count_fifo_7, 
                local_shift_data_7_0, local_shift_data_7_1, local_shift_data_7_2, local_shift_data_7_3, 
                local_shift_data_7_4, local_shift_data_7_5, local_shift_data_7_6, local_shift_data_7_7, 
                local_shift_len_7_0, local_shift_len_7_1, local_shift_len_7_2, local_shift_len_7_3, 
                local_shift_len_7_4, local_shift_len_7_5, local_shift_len_7_6, local_shift_len_7_7);


    // phase 4: local group
    local_group(line_num, local_shift_data_0_0, local_shift_len_0_0, local_group_0_0);
    local_group(line_num, local_shift_data_0_1, local_shift_len_0_1, local_group_0_1);
    local_group(line_num, local_shift_data_0_2, local_shift_len_0_2, local_group_0_2);
    local_group(line_num, local_shift_data_0_3, local_shift_len_0_3, local_group_0_3);
    local_group(line_num, local_shift_data_0_4, local_shift_len_0_4, local_group_0_4);
    local_group(line_num, local_shift_data_0_5, local_shift_len_0_5, local_group_0_5);
    local_group(line_num, local_shift_data_0_6, local_shift_len_0_6, local_group_0_6);
    local_group(line_num, local_shift_data_0_7, local_shift_len_0_7, local_group_0_7);

    local_group(line_num, local_shift_data_1_0, local_shift_len_1_0, local_group_1_0);
    local_group(line_num, local_shift_data_1_1, local_shift_len_1_1, local_group_1_1);
    local_group(line_num, local_shift_data_1_2, local_shift_len_1_2, local_group_1_2);
    local_group(line_num, local_shift_data_1_3, local_shift_len_1_3, local_group_1_3);
    local_group(line_num, local_shift_data_1_4, local_shift_len_1_4, local_group_1_4);
    local_group(line_num, local_shift_data_1_5, local_shift_len_1_5, local_group_1_5);
    local_group(line_num, local_shift_data_1_6, local_shift_len_1_6, local_group_1_6);
    local_group(line_num, local_shift_data_1_7, local_shift_len_1_7, local_group_1_7);

    local_group(line_num, local_shift_data_2_0, local_shift_len_2_0, local_group_2_0);
    local_group(line_num, local_shift_data_2_1, local_shift_len_2_1, local_group_2_1);
    local_group(line_num, local_shift_data_2_2, local_shift_len_2_2, local_group_2_2);
    local_group(line_num, local_shift_data_2_3, local_shift_len_2_3, local_group_2_3);
    local_group(line_num, local_shift_data_2_4, local_shift_len_2_4, local_group_2_4);
    local_group(line_num, local_shift_data_2_5, local_shift_len_2_5, local_group_2_5);
    local_group(line_num, local_shift_data_2_6, local_shift_len_2_6, local_group_2_6);
    local_group(line_num, local_shift_data_2_7, local_shift_len_2_7, local_group_2_7);

    local_group(line_num, local_shift_data_3_0, local_shift_len_3_0, local_group_3_0);
    local_group(line_num, local_shift_data_3_1, local_shift_len_3_1, local_group_3_1);
    local_group(line_num, local_shift_data_3_2, local_shift_len_3_2, local_group_3_2);
    local_group(line_num, local_shift_data_3_3, local_shift_len_3_3, local_group_3_3);
    local_group(line_num, local_shift_data_3_4, local_shift_len_3_4, local_group_3_4);
    local_group(line_num, local_shift_data_3_5, local_shift_len_3_5, local_group_3_5);
    local_group(line_num, local_shift_data_3_6, local_shift_len_3_6, local_group_3_6);
    local_group(line_num, local_shift_data_3_7, local_shift_len_3_7, local_group_3_7);

    local_group(line_num, local_shift_data_4_0, local_shift_len_4_0, local_group_4_0);
    local_group(line_num, local_shift_data_4_1, local_shift_len_4_1, local_group_4_1);
    local_group(line_num, local_shift_data_4_2, local_shift_len_4_2, local_group_4_2);
    local_group(line_num, local_shift_data_4_3, local_shift_len_4_3, local_group_4_3);
    local_group(line_num, local_shift_data_4_4, local_shift_len_4_4, local_group_4_4);
    local_group(line_num, local_shift_data_4_5, local_shift_len_4_5, local_group_4_5);
    local_group(line_num, local_shift_data_4_6, local_shift_len_4_6, local_group_4_6);
    local_group(line_num, local_shift_data_4_7, local_shift_len_4_7, local_group_4_7);

    local_group(line_num, local_shift_data_5_0, local_shift_len_5_0, local_group_5_0);
    local_group(line_num, local_shift_data_5_1, local_shift_len_5_1, local_group_5_1);
    local_group(line_num, local_shift_data_5_2, local_shift_len_5_2, local_group_5_2);
    local_group(line_num, local_shift_data_5_3, local_shift_len_5_3, local_group_5_3);
    local_group(line_num, local_shift_data_5_4, local_shift_len_5_4, local_group_5_4);
    local_group(line_num, local_shift_data_5_5, local_shift_len_5_5, local_group_5_5);
    local_group(line_num, local_shift_data_5_6, local_shift_len_5_6, local_group_5_6);
    local_group(line_num, local_shift_data_5_7, local_shift_len_5_7, local_group_5_7);

    local_group(line_num, local_shift_data_6_0, local_shift_len_6_0, local_group_6_0);
    local_group(line_num, local_shift_data_6_1, local_shift_len_6_1, local_group_6_1);
    local_group(line_num, local_shift_data_6_2, local_shift_len_6_2, local_group_6_2);
    local_group(line_num, local_shift_data_6_3, local_shift_len_6_3, local_group_6_3);
    local_group(line_num, local_shift_data_6_4, local_shift_len_6_4, local_group_6_4);
    local_group(line_num, local_shift_data_6_5, local_shift_len_6_5, local_group_6_5);
    local_group(line_num, local_shift_data_6_6, local_shift_len_6_6, local_group_6_6);
    local_group(line_num, local_shift_data_6_7, local_shift_len_6_7, local_group_6_7);

    local_group(line_num, local_shift_data_7_0, local_shift_len_7_0, local_group_7_0);
    local_group(line_num, local_shift_data_7_1, local_shift_len_7_1, local_group_7_1);
    local_group(line_num, local_shift_data_7_2, local_shift_len_7_2, local_group_7_2);
    local_group(line_num, local_shift_data_7_3, local_shift_len_7_3, local_group_7_3);
    local_group(line_num, local_shift_data_7_4, local_shift_len_7_4, local_group_7_4);
    local_group(line_num, local_shift_data_7_5, local_shift_len_7_5, local_group_7_5);
    local_group(line_num, local_shift_data_7_6, local_shift_len_7_6, local_group_7_6);
    local_group(line_num, local_shift_data_7_7, local_shift_len_7_7, local_group_7_7);


    // phase 5: concatenate each bucket to its corresponding buffers
    concat_engine(local_group_0_0, local_group_1_0, local_group_2_0, local_group_3_0, 
                    local_group_4_0, local_group_5_0, local_group_6_0, local_group_7_0, out_fifo_0);
    
    concat_engine(local_group_0_1, local_group_1_1, local_group_2_1, local_group_3_1, 
                    local_group_4_1, local_group_5_1, local_group_6_1, local_group_7_1, out_fifo_1);
    
    concat_engine(local_group_0_2, local_group_1_2, local_group_2_2, local_group_3_2, 
                    local_group_4_2, local_group_5_2, local_group_6_2, local_group_7_2, out_fifo_2);

    concat_engine(local_group_0_3, local_group_1_3, local_group_2_3, local_group_3_3, 
                    local_group_4_3, local_group_5_3, local_group_6_3, local_group_7_3, out_fifo_3);

    concat_engine(local_group_0_4, local_group_1_4, local_group_2_4, local_group_3_4, 
                    local_group_4_4, local_group_5_4, local_group_6_4, local_group_7_4, out_fifo_4);

    concat_engine(local_group_0_5, local_group_1_5, local_group_2_5, local_group_3_5, 
                    local_group_4_5, local_group_5_5, local_group_6_5, local_group_7_5, out_fifo_5);
    
    concat_engine(local_group_0_6, local_group_1_6, local_group_2_6, local_group_3_6, 
                    local_group_4_6, local_group_5_6, local_group_6_6, local_group_7_6, out_fifo_6);
    
    concat_engine(local_group_0_7, local_group_1_7, local_group_2_7, local_group_3_7, 
                    local_group_4_7, local_group_5_7, local_group_6_7, local_group_7_7, out_fifo_7);

    // phase 6: write data back to off-chip memory
    write_engine (out_fifo_0, out0);
    write_engine (out_fifo_1, out1);
    write_engine (out_fifo_2, out2);
    write_engine (out_fifo_3, out3);
    write_engine (out_fifo_4, out4);
    write_engine (out_fifo_5, out5);
    write_engine (out_fifo_6, out6);
    write_engine (out_fifo_7, out7);
    

}
}