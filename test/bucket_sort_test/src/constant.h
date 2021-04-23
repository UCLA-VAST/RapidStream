#ifndef CONSTANT_H
#define CONSTANT_H
#include <math.h>
#include "ap_int.h"
#include "hls_stream.h"


#define RECORD_WIDTH 32
#define BUS_WIDTH 256
#define RECORD_NUM BUS_WIDTH/RECORD_WIDTH

#define BUCKET_NUM 8
#define BUCKET_BITS (int)(log2 ((double)BUCKET_NUM))

#define WRITE_BURST 64

// for test
#define NUM_LINE 8192
#define BUCKET_MSB (int)(log2 ((double)(NUM_LINE*RECORD_NUM)))

#define DIV_CEIL(x, base) (((x) + (base) - 1 ) / (base))

typedef ap_uint<1> uint1;
typedef ap_uint<2> uint2;
typedef ap_uint<3> uint3;
typedef ap_uint<8> uint8;
typedef ap_uint<32> uint32;


typedef ap_uint<RECORD_WIDTH>   record_t;
typedef ap_uint<BUS_WIDTH>      bus_t;
typedef ap_uint<2*BUS_WIDTH>    bus_2t;
typedef ap_uint<8*BUCKET_NUM>   count_t;


void bitonic_sort (hls::stream<bus_t> &data_in, hls::stream<bus_t> &data_out, hls::stream<count_t> &count_out, int line_num);

void local_shift (int line_num, hls::stream<bus_t> &data_in, hls::stream<count_t> &count_in, 
                    hls::stream<bus_t> &data_out_0, hls::stream<bus_t> &data_out_1, hls::stream<bus_t> &data_out_2, hls::stream<bus_t> &data_out_3, 
                    hls::stream<bus_t> &data_out_4, hls::stream<bus_t> &data_out_5, hls::stream<bus_t> &data_out_6, hls::stream<bus_t> &data_out_7, 
                    hls::stream<uint8> &count_out_0, hls::stream<uint8> &count_out_1, hls::stream<uint8> &count_out_2, hls::stream<uint8> &count_out_3, 
                    hls::stream<uint8> &count_out_4, hls::stream<uint8> &count_out_5, hls::stream<uint8> &count_out_6, hls::stream<uint8> &count_out_7);

void local_group (int line_num, hls::stream<bus_t> &stream_in, hls::stream<uint8> &length, hls::stream<bus_t> &stream_out);

void concat_engine(hls::stream<bus_t> &in0, hls::stream<bus_t> &in1, hls::stream<bus_t> &in2, hls::stream<bus_t> &in3, 
                   hls::stream<bus_t> &in4, hls::stream<bus_t> &in5, hls::stream<bus_t> &in6, hls::stream<bus_t> &in7,  hls::stream<bus_t> &out);

extern "C" {
void bucket_sort(bus_t* in0,  bus_t* in1,  bus_t* in2,  bus_t* in3, 
                 bus_t* in4,  bus_t* in5,  bus_t* in6,  bus_t* in7, 
                 bus_t* out0, bus_t* out1, bus_t* out2, bus_t* out3,
                 bus_t* out4, bus_t* out5, bus_t* out6, bus_t* out7, int data_size);
}

#endif