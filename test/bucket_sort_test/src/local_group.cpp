#include "constant.h"

using namespace hls;

void local_group(int line_num, hls::stream<bus_t> &stream_in, hls::stream<uint8> &length, hls::stream<bus_t> &stream_out) {

    int i;
    uint8 current_pos = 0;

    // bus_t bit_mask = (record_t)(0 - 1);
    bus_2t pack_temp = 0;

    for (i = 0; i < line_num; i++) {
#pragma HLS pipeline II=1
        bus_t data_in;
        uint8 length_in;

        bus_t lower_half;
        bus_t higher_half;


        if (stream_in.empty() || length.empty()) {
            i--; 
            continue;
        }

        // load data from input streams
        stream_in.read_nb(data_in);
        length.read_nb(length_in);
        
        uint8 old_pos = current_pos;
        uint8 new_pos = current_pos + length_in;
        pack_temp |= ((bus_2t)data_in << (old_pos * RECORD_WIDTH));
        lower_half = pack_temp(BUS_WIDTH-1, 0);
        higher_half = pack_temp(2*BUS_WIDTH-1, BUS_WIDTH);

        if (new_pos >= RECORD_NUM) { // need to write out lower half
            current_pos = new_pos - RECORD_NUM;
            stream_out.write(lower_half);
            pack_temp = (bus_2t)higher_half;
        } else {
            current_pos = new_pos;
        }
    }
    // write out the rest & assert group_done
    // stream_out.write(pack_temp(BUS_WIDTH-1, 0)); // ideally 
    stream_out.write((bus_t)0);
}