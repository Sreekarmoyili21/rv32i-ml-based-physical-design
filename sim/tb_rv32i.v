`timescale 1ns / 1ps

module tb_rv32i;
    reg clk;
    reg reset;
    wire [31:0] imem_addr, dmem_addr, dmem_wdata;
    reg  [31:0] imem_rdata, dmem_rdata;
    wire        dmem_we;

    rv32i_core uut (
        .clk(clk), .reset(reset),
        .imem_addr(imem_addr), .imem_rdata(imem_rdata),
        .dmem_addr(dmem_addr), .dmem_wdata(dmem_wdata),
        .dmem_rdata(dmem_rdata), .dmem_we(dmem_we)
    );

    always #5 clk = ~clk;

    reg [31:0] imem [0:255];
    reg [31:0] dmem [0:255];

    always @(*) imem_rdata = imem[imem_addr[9:2]];
    always @(posedge clk) if (dmem_we) dmem[dmem_addr[9:2]] <= dmem_wdata;
    always @(*) dmem_rdata = dmem[dmem_addr[9:2]];

    initial begin
        $dumpfile("sim/wave.vcd");
        $dumpvars(0, tb_rv32i);

        clk = 0; reset = 1;

        imem[0] = 32'h00a00093; // ADDI x1, x0, 10  (x1 = 10)
        imem[1] = 32'h01900113; // ADDI x2, x0, 25  (x2 = 25)
        imem[2] = 32'h002081b3; // ADD  x3, x1, x2  (x3 = 10 + 25 = 35)
        imem[3] = 32'h40110233; // SUB  x4, x2, x1  (x4 = 25 - 10 = 15)
        imem[4] = 32'h00302023; // SW   x3, 0(x0)   (Store 35 into memory)
        imem[5] = 32'h00002383; // LW   x7, 0(x0)   (Load 35 into x7)

        #20 reset = 0;
        #150;

        $display("----------------------------------------");
        $display("SIMULATION FINISHED SUCCESSFULLY!");
        $display("Register x1: %0d (Expected: 10)", uut.registers[1]);
        $display("Register x2: %0d (Expected: 25)", uut.registers[2]);
        $display("Register x3: %0d (Expected: 35)", uut.registers[3]);
        $display("Register x4: %0d (Expected: 15)", uut.registers[4]);
        $display("Register x7: %0d (Expected: 35 via RAM)", uut.registers[7]);
        $display("Waveform saved to: sim/wave.vcd");
        $display("----------------------------------------");
        $finish;
    end
endmodule
