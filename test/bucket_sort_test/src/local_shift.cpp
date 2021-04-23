#include "constant.h"

void cal_prefix_sum (bus_t data_in, count_t count_in, bus_t *data_out, count_t *count_out, count_t *prefix_sum, count_t *suffix_sum) 
{
#pragma HLS interface ap_none port=data_out register
#pragma HLS interface ap_none port=count_out register
#pragma HLS interface ap_none port=prefix_sum register
#pragma HLS interface ap_none port=suffix_sum register
    uint8 length[BUCKET_NUM];
#pragma HLS array_partition variable=length complete
    uint8 sum_prefix[BUCKET_NUM];
#pragma HLS array_partition variable=sum_prefix complete
    uint8 sum_suffix[BUCKET_NUM];
#pragma HLS array_partition variable=sum_suffix complete

    int i, j;

    // convert count_t-wide data into an array of length[i]
    for (i = 0; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        length[i] = count_in((i+1)*8-1, i*8);
    }

    // calculate prefix_sum
    sum_prefix[0] = 0;
    sum_prefix[1] = length[0];
    sum_prefix[2] = length[0] + length[1];
    sum_prefix[3] = length[0] + length[1] + length[2];
    sum_prefix[4] = length[0] + length[1] + length[2] + length[3];
    sum_prefix[5] = length[0] + length[1] + length[2] + length[3] + length[4];
    sum_prefix[6] = length[0] + length[1] + length[2] + length[3] + length[4] + length[5];
    sum_prefix[7] = length[0] + length[1] + length[2] + length[3] + length[4] + length[5] + length[6];
    /*
    sum_prefix[0] = 0;
    for (i = 1; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        for (j = 0; j < i; j++) {
#pragma HLS unroll
            sum_prefix[i] += length[j];
        }
    }
    */

    // calculate suffix_sum
    sum_suffix[7] = 0;
    sum_suffix[6] = length[7];
    sum_suffix[5] = length[7] + length[6];
    sum_suffix[4] = length[7] + length[6] + length[5];
    sum_suffix[3] = length[7] + length[6] + length[5] + length[4];
    sum_suffix[2] = length[7] + length[6] + length[5] + length[4] + length[3];
    sum_suffix[1] = length[7] + length[6] + length[5] + length[4] + length[3] + length[2];
    sum_suffix[0] = length[7] + length[6] + length[5] + length[4] + length[3] + length[2] + length[1];
    /*
    sum_suffix[BUCKET_NUM-1] = 0;
    for (i = 0; i < BUCKET_NUM-1; i++) {
#pragma HLS unroll
        for (j = BUCKET_NUM-1; j > i; j--) {
#pragma HLS unroll
            sum_suffix[i] += length[j];
        }
    }
    */

    count_t temp_prefix;
    for (i = 0; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        temp_prefix((i+1)*8-1, i*8) = sum_prefix[i];
    }

    count_t temp_suffix;
    for (i = 0; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        temp_suffix((i+1)*8-1, i*8) = sum_suffix[i];
    }

    *data_out = data_in;
    *count_out = count_in;
    *prefix_sum = temp_prefix;
    *suffix_sum = temp_suffix;
}

void gen_shift(bus_t data_in, count_t count_in, count_t prefix_sum_in, count_t suffix_sum_in, 
                bus_t *data_out_0, bus_t *data_out_1, bus_t *data_out_2, bus_t *data_out_3, 
                bus_t *data_out_4, bus_t *data_out_5, bus_t *data_out_6, bus_t *data_out_7, count_t *count_out)
{
#pragma HLS interface ap_none port=data_out_0 register
#pragma HLS interface ap_none port=data_out_1 register
#pragma HLS interface ap_none port=data_out_2 register
#pragma HLS interface ap_none port=data_out_3 register
#pragma HLS interface ap_none port=count_out register

uint8 sum_prefix[BUCKET_NUM];
#pragma HLS array_partition variable=sum_prefix complete
uint8 sum_suffix[BUCKET_NUM];
#pragma HLS array_partition variable=sum_suffix complete

    bus_t bit_mask0 = (bus_t)(0 - 1);
    bus_t bit_mask1 = (bus_t)(0 - 1);
    bus_t bit_mask2 = (bus_t)(0 - 1);
    bus_t bit_mask3 = (bus_t)(0 - 1);
    bus_t bit_mask4 = (bus_t)(0 - 1);
    bus_t bit_mask5 = (bus_t)(0 - 1);
    bus_t bit_mask6 = (bus_t)(0 - 1);
    bus_t bit_mask7;

    int i;

    // convert count_t-wide data into an array of length[i]
    for (i = 0; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        sum_prefix[i] = prefix_sum_in((i+1)*8-1, i*8);
    }
    for (i = 0; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        sum_suffix[i] = suffix_sum_in((i+1)*8-1, i*8);
    }

    bit_mask0 = bit_mask0 >> (sum_suffix[0] * RECORD_WIDTH);
    bit_mask1 = bit_mask1 >> (sum_suffix[1] * RECORD_WIDTH);
    bit_mask2 = bit_mask2 >> (sum_suffix[2] * RECORD_WIDTH);
    bit_mask3 = bit_mask3 >> (sum_suffix[3] * RECORD_WIDTH);
    bit_mask4 = bit_mask4 >> (sum_suffix[4] * RECORD_WIDTH);
    bit_mask5 = bit_mask5 >> (sum_suffix[5] * RECORD_WIDTH);
    bit_mask6 = bit_mask6 >> (sum_suffix[6] * RECORD_WIDTH);
    // bit_mask7 doesnt need to shift

    bit_mask0 &= data_in;
    bit_mask1 &= data_in;
    bit_mask2 &= data_in;
    bit_mask3 &= data_in;
    bit_mask4 &= data_in;
    bit_mask5 &= data_in;
    bit_mask6 &= data_in;
    bit_mask7 = data_in;

    // shift
    bit_mask1 = bit_mask1 >> (sum_prefix[1] * RECORD_WIDTH);
    bit_mask2 = bit_mask2 >> (sum_prefix[2] * RECORD_WIDTH);
    bit_mask3 = bit_mask3 >> (sum_prefix[3] * RECORD_WIDTH);
    bit_mask4 = bit_mask4 >> (sum_prefix[4] * RECORD_WIDTH);
    bit_mask5 = bit_mask5 >> (sum_prefix[5] * RECORD_WIDTH);
    bit_mask6 = bit_mask6 >> (sum_prefix[6] * RECORD_WIDTH);
    bit_mask7 = bit_mask7 >> (sum_prefix[7] * RECORD_WIDTH);

    *data_out_0 = bit_mask0;
    *data_out_1 = bit_mask1;
    *data_out_2 = bit_mask2;
    *data_out_3 = bit_mask3;
    *data_out_4 = bit_mask4;
    *data_out_5 = bit_mask5;
    *data_out_6 = bit_mask6;
    *data_out_7 = bit_mask7;
    *count_out = count_in;
}

void local_shift (int line_num, hls::stream<bus_t> &data_in, hls::stream<count_t> &count_in, 
                    hls::stream<bus_t> &data_out_0, hls::stream<bus_t> &data_out_1, hls::stream<bus_t> &data_out_2, hls::stream<bus_t> &data_out_3, 
                    hls::stream<bus_t> &data_out_4, hls::stream<bus_t> &data_out_5, hls::stream<bus_t> &data_out_6, hls::stream<bus_t> &data_out_7, 
                    hls::stream<uint8> &count_out_0, hls::stream<uint8> &count_out_1, hls::stream<uint8> &count_out_2, hls::stream<uint8> &count_out_3, 
                    hls::stream<uint8> &count_out_4, hls::stream<uint8> &count_out_5, hls::stream<uint8> &count_out_6, hls::stream<uint8> &count_out_7)
{
    for (int i = 0; i < line_num; i++) {
#pragma HLS pipeline II=1
        bus_t in_data;
        count_t in_count;

        bus_t data_l1;
        count_t count_l1;
        count_t prefix_sum;
        count_t suffix_sum;

        bus_t temp_out_0;
        bus_t temp_out_1;
        bus_t temp_out_2;
        bus_t temp_out_3;
        bus_t temp_out_4;
        bus_t temp_out_5;
        bus_t temp_out_6;
        bus_t temp_out_7;
        count_t count_out;

        if (data_in.empty() || count_in.empty()) {
            i--; 
            continue;
        }

        // load data
        data_in.read_nb(in_data);
        count_in.read_nb(in_count);

        cal_prefix_sum(in_data, in_count, &data_l1, &count_l1, &prefix_sum, &suffix_sum);
        gen_shift(data_l1, count_l1, prefix_sum, suffix_sum, &temp_out_0, &temp_out_1, &temp_out_2, 
                    &temp_out_3, &temp_out_4, &temp_out_5, &temp_out_6, &temp_out_7, &count_out);

        data_out_0.write(temp_out_0);
        data_out_1.write(temp_out_1);
        data_out_2.write(temp_out_2);
        data_out_3.write(temp_out_3);
        data_out_4.write(temp_out_4);
        data_out_5.write(temp_out_5);
        data_out_6.write(temp_out_6);
        data_out_7.write(temp_out_7);

        count_out_0.write(count_out(7, 0));
        count_out_1.write(count_out(15, 8));
        count_out_2.write(count_out(23, 16));
        count_out_3.write(count_out(31, 24));
        count_out_4.write(count_out(39, 32));
        count_out_5.write(count_out(47, 40));
        count_out_6.write(count_out(55, 48));
        count_out_7.write(count_out(63, 56));
    }

}