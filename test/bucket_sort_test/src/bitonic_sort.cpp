#include "constant.h"

// swap 1 return the smaller value
record_t swap1(record_t in_1, record_t in_2) {
#pragma HLS inline
    return (in_1 > in_2) ? in_2 : in_1;
}

// swap 2 return the smaller value
record_t swap2(record_t in_1, record_t in_2) {
#pragma HLS inline
    return (in_1 > in_2) ? in_1 : in_2;
}

void bitonic_sort_level1 (bus_t data_in, bus_t *data_out)
{
#pragma HLS interface ap_none port=data_out register
    record_t input[RECORD_NUM];
    record_t sort_data[RECORD_NUM];
#pragma HLS array_partition variable=input complete
#pragma HLS array_partition variable=sort_data complete

    int i;
    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }

    for (i = 0; i < RECORD_NUM; i = i + 2) {
#pragma HLS unroll
        if (i % 4 == 0) {
            sort_data[i] = swap1(input[i], input[i+1]);
            sort_data[i+1] = swap2(input[i], input[i+1]);
        } else {
            sort_data[i] = swap2(input[i], input[i+1]);
            sort_data[i+1] = swap1(input[i], input[i+1]);
        }
    }

    bus_t temp;
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS UNROLL
        temp((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH) = sort_data[i];
    }
    
    *data_out = temp;
}


void bitonic_sort_level2 (bus_t data_in, bus_t *data_out)
{
#pragma HLS interface ap_none port=data_out register
    record_t input[RECORD_NUM];
    record_t sort_data[RECORD_NUM];
#pragma HLS array_partition variable=input complete
#pragma HLS array_partition variable=sort_data complete

    int i;
    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }

    for (i = 0; i < RECORD_NUM; i = i + 4) {
#pragma HLS unroll
        if (i % 8 < 4) {
            sort_data[i] = swap1(input[i], input[i+2]);
            sort_data[i+2] = swap2(input[i], input[i+2]);
            sort_data[i+1] = swap1(input[i+1], input[i+3]);
            sort_data[i+3] = swap2(input[i+1], input[i+3]);
        } else {
            sort_data[i] = swap2(input[i], input[i+2]);
            sort_data[i+2] = swap1(input[i], input[i+2]);
            sort_data[i+1] = swap2(input[i+1], input[i+3]);
            sort_data[i+3] = swap1(input[i+1], input[i+3]);
        }
    }

    bus_t temp;
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS UNROLL
        temp((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH) = sort_data[i];
    }
    
    *data_out = temp;
}


void bitonic_sort_level3 (bus_t data_in, bus_t *data_out)
{
#pragma HLS interface ap_none port=data_out register
    record_t input[RECORD_NUM];
    record_t sort_data[RECORD_NUM];
#pragma HLS array_partition variable=input complete
#pragma HLS array_partition variable=sort_data complete

    int i;
    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }


    for (i = 0; i < RECORD_NUM; i = i + 4) {
#pragma HLS unroll
        if (i % 8 < 4) {
            sort_data[i] = swap1(input[i], input[i+1]);
            sort_data[i+1] = swap2(input[i], input[i+1]);
            sort_data[i+2] = swap1(input[i+2], input[i+3]);
            sort_data[i+3] = swap2(input[i+2], input[i+3]);
        } else {
            sort_data[i] = swap2(input[i], input[i+1]);
            sort_data[i+1] = swap1(input[i], input[i+1]);
            sort_data[i+2] = swap2(input[i+2], input[i+3]);
            sort_data[i+3] = swap1(input[i+2], input[i+3]);
        }
    }

    bus_t temp;
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS UNROLL
        temp((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH) = sort_data[i];
    }
    
    *data_out = temp;
}


void bitonic_sort_level4 (bus_t data_in, bus_t *data_out)
{
#pragma HLS interface ap_none port=data_out register
    record_t input[RECORD_NUM];
    record_t sort_data[RECORD_NUM];
#pragma HLS array_partition variable=input complete
#pragma HLS array_partition variable=sort_data complete

    int i, j;
    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }


    for (i = 0; i < RECORD_NUM/2; i++) {
        sort_data[i] = swap1(input[i], input[i+4]);
        sort_data[i+4] = swap2(input[i], input[i+4]);
    }

    bus_t temp;
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS UNROLL
        temp((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH) = sort_data[i];
    }
    
    *data_out = temp;
}


void bitonic_sort_level5 (bus_t data_in, bus_t *data_out)
{
#pragma HLS interface ap_none port=data_out register
    record_t input[RECORD_NUM];
    record_t sort_data[RECORD_NUM];
#pragma HLS array_partition variable=input complete
#pragma HLS array_partition variable=sort_data complete

    int i, j;
    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }

    for (i = 0; i < RECORD_NUM; i = i + 4) {
        for (j = 0; j < 2; j++) {
            sort_data[i+j] = swap1(input[i+j], input[i+j+2]);
            sort_data[i+j+2] = swap2(input[i+j], input[i+j+2]);
        }
    }

    bus_t temp;
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS UNROLL
        temp((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH) = sort_data[i];
    }
    
    *data_out = temp;
}


void bitonic_sort_level6 (bus_t data_in, bus_t *data_out)
{
#pragma HLS interface ap_none port=data_out register
    record_t input[RECORD_NUM];
    record_t sort_data[RECORD_NUM];
#pragma HLS array_partition variable=input complete
#pragma HLS array_partition variable=sort_data complete

    int i, j;
    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }

    for (i = 0; i < RECORD_NUM / 2; i++) {
        sort_data[i*2] = swap1(input[i*2], input[i*2+1]);
        sort_data[i*2+1] = swap2(input[i*2], input[i*2+1]);
    }

    bus_t temp;
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS UNROLL
        temp((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH) = sort_data[i];
    }
    
    *data_out = temp;
}


void dummy_delay(count_t count_in, count_t *count_out) // dummy delay is used to delay one cycle
{
#pragma HLS interface ap_none port=count_out register
    *count_out = count_in;
}


void length_count (bus_t data_in, count_t *count_out) // This version is a simple bucketing based on BUCKET_BITS-MSBs
{
#pragma HLS interface ap_none port=count_out register

    record_t input[RECORD_NUM];
#pragma HLS array_partition variable=input complete
    //uint1 valid[RECORD_NUM*BUCKET_NUM];
    uint1 valid[RECORD_NUM][BUCKET_NUM];
#pragma HLS array_partition variable=valid complete
    uint8 length[BUCKET_NUM];
#pragma HLS array_partition variable=length complete

    int i, j;

    // convert bus_t-wide data into an array of inputs
    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        input[i] = data_in((i+1)*RECORD_WIDTH-1, i*RECORD_WIDTH);
    }

    for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
        for (j = 0; j < BUCKET_NUM; j++) {
#pragma HLS unroll
            valid[i][j] = (input[i](BUCKET_MSB+BUCKET_BITS - 1, BUCKET_MSB) == j) ? 1 : 0;  // modify here
        }
    }
    

    for (j = 0; j < BUCKET_NUM; j++) {
#pragma HLS unroll
        length[j] = 0;
        for (i = 0; i < RECORD_NUM; i++) {
#pragma HLS unroll
            length[j] += valid[i][j];
        }
    }

    count_t temp;
    for (i = 0; i < BUCKET_NUM; i++) {
#pragma HLS unroll
        temp((i+1)*8-1, i*8) = length[i];
    }

    *count_out = temp;
}


void bitonic_sort (hls::stream<bus_t> &data_in, hls::stream<bus_t> &data_out, hls::stream<count_t> &count_out, int line_num)
{

    for (int i = 0; i < line_num; i++) {
#pragma HLS pipeline II=1
        bus_t in_data;
        bus_t sort_l1;
        bus_t sort_l2;
        bus_t sort_l3;
        bus_t sort_l4;
        bus_t sort_l5;
        bus_t sort_l6;

        // 10-cycle latency to match the latency of bitonic sorter
        // right now the simple length_count only has 1 cycle latency
        count_t cnt_l1;
        count_t cnt_l2;
        count_t cnt_l3;
        count_t cnt_l4;
        count_t cnt_l5;
        count_t cnt_l6;

        if (data_in.empty()) {
            i--; 
            continue;
        }

        // load data
        data_in.read_nb(in_data);

        // bitonic sort
        // level 1
        bitonic_sort_level1(in_data, &sort_l1);
        // level 2
        bitonic_sort_level2(sort_l1, &sort_l2);
        // level 3
        bitonic_sort_level3(sort_l2, &sort_l3);
        // level 4
        bitonic_sort_level4(sort_l3, &sort_l4);
        // level 5
        bitonic_sort_level5(sort_l4, &sort_l5);
        // level 6
        bitonic_sort_level6(sort_l5, &sort_l6);      
        data_out.write(sort_l6);

        // frequency count
        length_count (in_data, &cnt_l1);
        dummy_delay (cnt_l1, &cnt_l2);
        dummy_delay (cnt_l2, &cnt_l3);
        dummy_delay (cnt_l3, &cnt_l4);
        dummy_delay (cnt_l4, &cnt_l5);
        dummy_delay (cnt_l5, &cnt_l6);
        count_out.write(cnt_l6);
    }
}
