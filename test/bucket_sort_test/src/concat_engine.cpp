#include "constant.h"

void concat_engine(
    hls::stream<bus_t> &in0,
    hls::stream<bus_t> &in1,
    hls::stream<bus_t> &in2,
    hls::stream<bus_t> &in3,
    hls::stream<bus_t> &in4,
    hls::stream<bus_t> &in5,
    hls::stream<bus_t> &in6,
    hls::stream<bus_t> &in7,
    hls::stream<bus_t> &out
)
{
    uint1 end0 = 0; //endN = 1 indicate stream N has been entirely poped out
    uint1 end1 = 0;
    uint1 end2 = 0;
    uint1 end3 = 0;
    uint1 end4 = 0;
    uint1 end5 = 0;
    uint1 end6 = 0;
    uint1 end7 = 0;

    uint3 sel = 0;

    while (
        (end0 == 0) ||
        (end1 == 0) ||
        (end2 == 0) ||
        (end3 == 0) || 
        (end4 == 0) ||
        (end5 == 0) ||
        (end6 == 0) ||
        (end7 == 0)
    ) {
        bus_t temp;
        bool success;
        switch(sel) {
            case 0:
                if (end0 == 0) {
                    if (in0.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end0 = 1;
                        }
                    }
                }
                sel++;
                break;

            case 1:
                if (end1 == 0) {
                    if (in1.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end1 = 1;
                        }
                    }
                }
                sel++;
                break;

            case 2:
                if (end2 == 0) {
                    if (in2.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end2 = 1;
                        }
                    }
                }
                sel++;
                break;

            case 3:
                if (end3 == 0) {
                    if (in3.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end3 = 1;
                        }
                    }
                }
                sel++;
                break;

            case 4:
                if (end4 == 0) {
                    if (in4.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end4 = 1;
                        }
                    }
                }
                sel++;
                break;

            case 5:
                if (end5 == 0) {
                    if (in5.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end5 = 1;
                        }
                    }
                }
                sel++;
                break;
            
            case 6:
                if (end6 == 0) {
                    if (in6.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end6 = 1;
                        }
                    }
                }
                sel++;
                break;

            default:
                if (end7 == 0) {
                    if (in7.read_nb(temp)) {
                        if (temp(63, 0) != 0) {
                            out.write(temp);
                        } else {
                            end7 = 1;
                        }
                    }
                }
                sel = 0;
                break;
        }
    }
    out.write((bus_t)0);
}