#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>

#include "constant.h"

#define NO_ELEM NUM_LINE*RECORD_NUM

int main()
{
    std::cout << "check point 0\n";
    int i,j,k;

    bus_t source_in = 0;
    bus_t source_out = 0;
    
    bus_t* stream_in[BUCKET_NUM];
    bus_t* stream_out[BUCKET_NUM];
    
    int dataSize = NO_ELEM;

    record_t data_in[BUCKET_NUM][dataSize];
    record_t sort_data[BUCKET_NUM][dataSize];

    // create the test data
    for (i = 0; i < BUCKET_NUM; i++) {
        for (j = 0; j < BUCKET_NUM; j++) {
            for (k = 0; k < (NO_ELEM/BUCKET_NUM); k++) {
                data_in[i][j*NO_ELEM/BUCKET_NUM + k] = (j*BUCKET_NUM+i)*NO_ELEM/BUCKET_NUM + k;
            }
        }
    }
    
    
    for (i = 0; i < BUCKET_NUM; i++) {
        std::random_shuffle (data_in[i], data_in[i]+dataSize );
    }
    
    

    std::cout << "check point 1\n";

    // check input data
    std::ofstream inFILE[BUCKET_NUM];
    for (i = 0; i < BUCKET_NUM; i++) {
        inFILE[i].open("/curr/wkqiao/Alpha-Data/Vitis_Accel_Examples-2019.2/my_kernels/bucket_sort_v2/infile" + std::to_string(i));
        for (j = 0; j < dataSize; j++) {
            inFILE[i] << (unsigned int)data_in[i][j] << std::endl;
        }
        inFILE[i].close();
    }


    // prepare input streams
    for (i = 0; i < BUCKET_NUM; i++) {
        stream_in[i] = (bus_t*)malloc(NUM_LINE * sizeof(bus_t));
        stream_out[i] = (bus_t*)malloc(NUM_LINE * sizeof(bus_t));
        for (j = 0; j < NUM_LINE; j++) {
            for (k = RECORD_NUM - 1; k >= 0; k--) {
                source_in = (source_in << RECORD_WIDTH) + data_in[i][j*RECORD_NUM+k];
            }
            stream_in[i][j] =  source_in;
        }
    }

    std::cout << "check point 2\n";
    bucket_sort(stream_in[0], stream_in[1], stream_in[2], stream_in[3], stream_in[4], stream_in[5], stream_in[6], stream_in[7],
                stream_out[0], stream_out[1], stream_out[2], stream_out[3], stream_out[4], stream_out[5], stream_out[6], stream_out[7], dataSize);
    std::cout << "check point 3\n";
    

    for (i = 0; i < BUCKET_NUM; i++) {
        for (j = 0; j < NUM_LINE; j++) {
            source_out = stream_out[i][j];
            for (k = 0; k < RECORD_NUM; k++) {
                sort_data[i][j*RECORD_NUM+k] = source_out(RECORD_WIDTH-1, 0);
                source_out = source_out >> RECORD_WIDTH;
            }
        }
    }

    // write output data
    std::ofstream outFILE[BUCKET_NUM];
    for (i = 0; i < BUCKET_NUM; i++) {
        outFILE[i].open("./outfile/output" + std::to_string(i));
        for (j = 0; j < dataSize; j++) {
            outFILE[i] << (unsigned int)sort_data[i][j] << std::endl;
        }
        outFILE[i].close();
    }

    // check output data
    bool check_status = 0;
    for (i = 0; i < BUCKET_NUM; i++) {
        for (j = 0; j < dataSize; j++) {
            if ((sort_data[i][j] >= (i+1) * NO_ELEM) ||  sort_data[i][j] < i * NO_ELEM) {
                std::cout<< "group " << i << " element " << j << " : " << sort_data[i][j] << " is out of range\n";
                check_status = 1;
                break;
            }
        }
    }

    std::cout << "TEST " << (check_status ? "FAILED" : "PASSED") << std::endl;

    return 0;
}
