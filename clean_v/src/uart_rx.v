`timescale 1ns / 1ps
//asinchronic input
module uart_rx(

input clk,
input reset, 
input rx, //B18
output reg [7:0] data  = 0,  
output reg       valid = 0   
    );
    

// constants
parameter clk_freq = 100000000;  
parameter baud_rate = 921600; 
localparam integer BIT  = clk_freq / baud_rate;
localparam integer HALF = BIT / 2;

reg rx1 = 1, rx2 = 1, rx3 =1;

always @(posedge clk) begin
    rx1 <= rx;
    rx2 <= rx1;
    rx3 <= rx2; 
end

localparam 
IDLE = 0, 
START = 1, 
DATA = 2, 
STOP = 3;  // states

reg [1:0]  state = IDLE;
reg [13:0] count = 0;   
reg [2:0]  n     = 0;    
reg [7:0]  sh    = 0;    

always @(posedge clk) begin

    if (reset) begin
        state <= IDLE;
        count <= 0;
        n <= 0;
        sh <= 0;
        data <= 0;
        valid <= 0;
    end
    else begin

        valid <= 0;

        case (state)

            IDLE: begin
                count <= 0;
                if (rx3 == 1 && rx2 == 0)
                    state <= START;
            end

            START: begin
                if (count == HALF - 1) begin
                    count <= 0;

                    if (rx2 == 0) begin
                        n <= 0;
                        state <= DATA;
                    end
                    else
                        state <= IDLE;

                end
                else
                    count <= count + 1;
            end

            DATA: begin
                if (count == BIT - 1) begin
                    count <= 0;
                    sh <= {rx2, sh[7:1]};
                    if (n == 7)
                        state <= STOP;
                    else
                        n <= n + 1;
                end
                else
                    count <= count + 1;
            end

            STOP: begin
                if (count == BIT - 1) begin
                    count <= 0;

                    if (rx2 == 1) begin
                        data <= sh;
                        valid <= 1;
                    end

                    state <= IDLE;
                end
                else
                    count <= count + 1;
            end

            default: state <= IDLE;
        endcase
    end
end
endmodule
