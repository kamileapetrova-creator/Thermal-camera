`timescale 1ns / 1ps
module uart_cmd (
    input            clk,
    input      [7:0] rx_data,
    input            rx_valid,
    output reg       set_x = 0,
    output reg       set_y = 0,
    output reg       set_z = 0,
    output reg [15:0] value = 0
);
    reg [1:0] state = 0;       
    reg [7:0] cmd   = 0;
    reg [7:0] hi    = 0; 

    always @(posedge clk) begin
        set_x <= 0; set_y <= 0; set_z <= 0;   
        if (rx_valid) begin
            case (state)
                0: begin                      
                    cmd   <= rx_data;
                    state <= 1;
                end
                1: begin                      
                    hi    <= rx_data;
                    state <= 2;
                end
                default: begin                 
                    value <= {hi, rx_data};
                    case (cmd)
                        "x":     set_x <= 1;
                        "y":     set_y <= 1;
                        "z":     set_z <= 1;
                        default: ;
                    endcase
                    state <= 0;
                end
            endcase      
        end    
    end
endmodule