module score_bar(
	input  logic       Clk, reset, frame_clk,
    input [9:0]        DrawX, DrawY,
    input [15:0]	   score,
    output logic 	   is_score	
);

logic [479:0] score_height;

int DistX, DistY, Size;
//assign DistX = DrawX - arrow_1_pos_x;
//assign DistY = DrawY - arrow_1_pos_y;
/*
assign DistX = DrawX - arrow_1_pos_x;
assign DistY = DrawY - arrow_1_pos_y;
assign Size = 4;
*/
logic frame_clk_delayed;
logic frame_clk_rising_edge;

always_ff @ (posedge Clk)
begin
    frame_clk_delayed <= frame_clk;
end
assign frame_clk_rising_edge = (frame_clk == 1'b1) && (frame_clk_delayed == 1'b0);

always_ff @ (posedge Clk)
begin
    if(reset)
    begin
    	score_height[239:0] = 240'b11;
    end
    else if(frame_clk_rising_edge)
    begin
    	for(int n=479; n>=0;n--)
    	begin
    		if((479-n) <= score >> 8)
    			score_height[n] = 1'b1;
    		else
    		begin
    			score_height[n] = 1'b0;
    		end	
    	end
    end
end

always_comb
begin
    is_score = 1'b0;
	   for(int n=0; n<480;n++)
		begin
		  if (score_height[n] == 1'b1)
			 if (DrawX >= 10'd480 && DrawX < 10'd500 && DrawY == n)//<= (n+Size) && DrawY >= (n-Size))
				is_score = 1'b1;		
		end
end


endmodule