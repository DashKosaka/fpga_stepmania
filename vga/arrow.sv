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
// module arrow (
// 	input  logic       Clk, reset, frame_clk,
// 	input [9:0]        DrawX, DrawY,
// 	output logic [3:0] display_arrow
// );

// // some static values
// parameter [9:0] arrow_center_x = 320-64;  // Center position on the X axis
// parameter [9:0] arrow_center_y = 240;  // Center position on the Y axis

// // position variables
// logic [9:0] x_pos, y_pos;   // position on screen of arrow
// logic [9:0] x_dist, y_dist; // distance from draw{X,Y} to center of arrow
// assign x_dist = DrawX - x_pos;
// assign y_dist = DrawY - y_pos;

// // timing
// logic frame_clk_delayed, frame_clk_rising_edge;
// always_ff @ (posedge Clk) begin
//     frame_clk_delayed <= frame_clk;
// end
// assign frame_clk_rising_edge = (frame_clk == 1'b1) && (frame_clk_delayed == 1'b0);

// // reset and every clock cycle behavior
// always_ff @ (posedge Clk) begin
//     if (reset)
//     begin
//         x_pos <= arrow_center_x;
//         y_pos <= arrow_center_y;
//         // Ball_X_Motion <= 10'd0;
//         // Ball_Y_Motion <= Ball_Y_Step;
//     end
//     else if (frame_clk_rising_edge)        // Update only at rising edge of frame clock
//     begin
//         // x_pos <= x_pos_in;
//         // Ball_Y_Pos <= Ball_Y_Pos_in;
//         // Ball_X_Motion <= Ball_X_Motion_in;
//         // Ball_Y_Motion <= Ball_Y_Motion_in;
//     end
//     // By defualt, keep the register values.
// end


// // output the draw signal
// always_comb begin
// 	display_arrow = 1'b0;
// 	if ( y_dist <= 32 && x_dist <= 32 )
// 		display_arrow[0] = 1'b1;
// end

// endmodule

module arrow (
    input  logic       Clk, reset, frame_clk,
    input [9:0]        DrawX, DrawY,
    output logic [3:0] display_arrow
);

// some static values
parameter [9:0] arrow_1_center_x = 272;
parameter [9:0] arrow_2_center_x = 304;
parameter [9:0] arrow_3_center_x = 336;
parameter [9:0] arrow_4_center_x = 368;
parameter [9:0] arrow_start_center_y = 16;
parameter [9:0] arrow_speed = 2;

logic [9:0] arrow_1_pos_x, arrow_1_pos_y, arrow_1_motion_y;
logic [9:0] arrow_1_pos_x_in, arrow_1_pos_y_in, arrow_1_motion_y_in;

int DistX, DistY, Size;
assign DistX = DrawX - arrow_1_pos_x;
assign DistY = DrawY - arrow_1_pos_y;
assign Size = 32;

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

always_comb
begin
    arrow_1_pos_x_in = arrow_1_pos_x;
    arrow_1_pos_y_in = arrow_1_pos_y + arrow_1_pos_y_in;
    arrow_1_pos_y_in = arrow_1_pos_y_in;
    arrow_1_pos_x_in = arrow_1_pos_x_in;
end

always_comb
begin
    display_arrow = 1'b0;
    if ( DistY <= 32 && DistX <= 32 )
        display_arrow[0] = 1'b1;    
end

endmodule