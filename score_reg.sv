module score_reg(
	input logic Clk,
	input logic frame_clk,
	input logic reset,
   input logic [3:0] hit0, hit1, hit2, hit3,
	input logic [3:0] miss0, miss1, miss2, miss3,
	output logic [15:0] score
);

logic [15:0] nextscore;
logic frame_clk_rising_edge;
logic frame_clk_delayed;

always_ff @ (posedge Clk)
begin
    frame_clk_delayed <= frame_clk;
end
assign frame_clk_rising_edge = (frame_clk == 1'b1) && (frame_clk_delayed == 1'b0);


always_ff @ (posedge Clk)
begin
	if(reset)
	begin
		score <= 15'b0;
	end
	
	else if(frame_clk_rising_edge)
	begin
		score <= score + + hit0 + hit1 + hit2 + hit3
		                  - miss0 - miss1 - miss2 - miss3;		
	end
	
end
/*
always_comb
begin
	nextscore = score + 1'b1;//hit0 + hit1 + hit2 + hit3
						//  - miss0 - miss1 - miss2 - miss3;
end
*/
endmodule