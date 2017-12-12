// module
// every tick (from input signal)
// read next value out of array

/*
    [0,0,1,0],
    [1,0,0,1]
*/

// if high, create arrow and place at bottom of screen

// draw arrows to screen
// current question: how can i draw multiple arrows to screen? how can i create a memory bank that draws new arrows on screen?
// how can i create a sprite on a screen?
// how can i create sprites by reading off a rom?
module arrow (
    input  logic       Clk, reset, frame_clk,
    input [9:0]        DrawX, DrawY,
	 input [3:0]        display_signal,
	 input [3:0]		  key_press,
    output logic [3:0] display_arrow,
	 output logic [3:0] hit0, hit1, hit2, hit3,
	 output logic [3:0] miss0, miss1, miss2, miss3
);

// some static values
parameter [9:0] arrow_1_center_x = 272;
parameter [9:0] arrow_2_center_x = 304;
parameter [9:0] arrow_3_center_x = 336;
parameter [9:0] arrow_4_center_x = 368;
parameter [9:0] arrow_start_center_y = 480-4;
parameter [9:0] arrow_speed = 2;

logic [9:0] arrow_1_pos_x, arrow_1_pos_y, arrow_1_motion_y;
logic [9:0] arrow_1_pos_x_in, arrow_1_pos_y_in, arrow_1_motion_y_in;
logic [479:0] arrow0_heights, arrow1_heights, arrow2_heights, arrow3_heights;

int DistX, DistY, Size;
//assign DistX = DrawX - arrow_1_pos_x;
//assign DistY = DrawY - arrow_1_pos_y;
assign DistX = DrawX - arrow_1_pos_x;
assign DistY = DrawY - arrow_1_pos_y;
assign Size = 4;

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
        arrow_1_pos_x <= arrow_1_center_x;
        arrow_1_pos_y <= arrow_start_center_y;
        arrow_1_motion_y <= 10'b0;
    end
    else if(frame_clk_rising_edge)
    begin
        arrow_1_pos_x <= arrow_1_pos_x_in;
        arrow_1_pos_y <= arrow_1_pos_y_in;
        arrow_1_motion_y <= arrow_1_motion_y_in;
    end
end

always_ff @ (posedge Clk)
begin
	 if(reset)
	 begin
		  arrow0_heights <= 479'b0;
		  arrow1_heights <= 479'b0;
		  arrow2_heights <= 479'b0;
		  arrow3_heights <= 479'b0;
 end
	 //arrow_heights <<= 1;
	 else if(frame_clk_rising_edge)
	 begin
		 for(int i=arrow_speed; i<480; i++)
		 begin
			  // ARROW 0
			  if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30 
						&& key_press[0] == 1'b1)
			  begin
					arrow0_heights[i-arrow_speed] <= 1'b0;
				   arrow0_heights[i] <= 1'b0;						
					//if(arrow0_heights[i] == 1'b1)begin hit0 <= 4'b1111;end
			  end
  			  else if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30 
						&& key_press[0] == 1'b1 && arrow0_heights[i] == 1'b1)
  			  begin
					arrow0_heights[i-arrow_speed] <= 1'b0;
				   arrow0_heights[i] <= 1'b0;						
					hit0 <= 4'b1111;
  			  end
			  else
			  begin
				   arrow0_heights[i-arrow_speed] <= arrow0_heights[i];
			      arrow0_heights[i] <= 1'b0;
					miss0 <= 1'b01;
			  end		  
			  
			  
			  // ARROW 1
			  if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30 
						&& key_press[1] == 1'b1)
			  begin
					arrow1_heights[i-arrow_speed] <= 1'b0;
				   arrow1_heights[i] <= 1'b0;						
					//if(arrow1_heights[i] == 1'b1)begin hit1 <= 4'b1111;end
			  end
			  else if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30 
						&& key_press[1] == 1'b1 && arrow1_heights[i] == 1'b1)
			  begin
					arrow1_heights[i-arrow_speed] <= 1'b0;
				    arrow1_heights[i] <= 1'b0;						
					hit1 <= 4'b1111;			  		
			  end
			  else
			  begin
				   arrow1_heights[i-arrow_speed] <= arrow1_heights[i];
				   arrow1_heights[i] <= 1'b0;			  
					miss1 <= 1'b01;
			  end		
			  
			  
			  
			  if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30 
						&& key_press[2] == 1'b1)
			  begin
					arrow2_heights[i-arrow_speed] <= 1'b0;
				   arrow2_heights[i] <= 1'b0;						
					//if(arrow2_heights[i] == 1'b1)begin hit2 <= 4'b1111;end
			  end
			  else if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30 
						&& key_press[2] == 1'b1 && arrow2_heights[i])
			  begin
					arrow2_heights[i-arrow_speed] <= 1'b0;
				    arrow2_heights[i] <= 1'b0;						
					hit2 <= 4'b1111;			  		
			  end
			  else
			  begin
				   arrow2_heights[i-arrow_speed] <= arrow2_heights[i];
				   arrow2_heights[i] <= 1'b0;	
					miss2 <= 1'b01;
			  end		
			  
			  
			  
			  if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30
						&& key_press[3] == 1'b1)
			  begin
					arrow3_heights[i-arrow_speed] <= 1'b0;
				   arrow3_heights[i] <= 1'b0;							
					//	if(arrow3_heights[i] == 1'b1)begin	hit3 <= 4'b1111;end
			  end
			  else if(i-arrow_speed < 10'd79 
					&& i-arrow_speed >= 10'd30
						&& key_press[3] == 1'b1 && arrow3_heights[i])
			  begin
					arrow3_heights[i-arrow_speed] <= 1'b0;
				    arrow3_heights[i] <= 1'b0;							
					hit3 <= 4'b1111;			  		
			  end
			  else
			  begin
				   arrow3_heights[i-arrow_speed] <= arrow3_heights[i];
				   arrow3_heights[i] <= 1'b0;			  
					miss3 <= 1'b01;
			  end		
			  
		 end
		 arrow0_heights[0] <= 1'b0;
		 arrow1_heights[0] <= 1'b0;
		 arrow2_heights[0] <= 1'b0;
		 arrow3_heights[0] <= 1'b0;

		 if(display_signal[0])
		 begin
			  arrow0_heights[479] <= 1'b1;
		 end
		 if(display_signal[1])
		 begin
			  arrow1_heights[479] <= 1'b1;
		 end
		 if(display_signal[2])
		 begin
			  arrow2_heights[479] <= 1'b1;
	    end
		 if(display_signal[3])
		 begin
			  arrow3_heights[479] <= 1'b1;
		 end
	 end
end

always_comb
begin
    display_arrow = 1'b0;
	   for(int n=0; n<480;n++)
		begin
		  if (arrow0_heights[n] == 1'b1)
			 if (DrawX >= 10'd256 && DrawX < 10'd288 && DrawY <= (n+Size) && DrawY >= (n-Size))
				display_arrow[0] = 1'b1;
		  if (arrow1_heights[n] == 1'b1)
			 if (DrawX >= 10'd288 && DrawX < 10'd320 && DrawY <= (n+Size) && DrawY >= (n-Size))
				display_arrow[1] = 1'b1;
		  if (arrow2_heights[n] == 1'b1)
			 if (DrawX >= 10'd320 && DrawX < 10'd352 && DrawY <= (n+Size) && DrawY >= (n-Size))
				display_arrow[2] = 1'b1;
		  if (arrow3_heights[n] == 1'b1)
			 if (DrawX >= 10'd352 && DrawX < 10'd384 && DrawY <= (n+Size) && DrawY >= (n-Size))
				display_arrow[3] = 1'b1;		
		end
end

endmodule

//make a couple of registers that store a current y-pos so every strip of arrows can be acounted for???
//if the output is not zero then

//whatif I made a 480 register or some kind of array
//for each pixel so that we can update every clock at which pixel a specific arrow strip
//is at.
/*use a for loop to check ever index and move it up one step
module y_reg(
		input logic 
);
*/