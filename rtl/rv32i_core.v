`timescale 1ns / 1ps

module rv32i_core (
    input  wire        clk,
    input  wire        reset,
    output wire [31:0] imem_addr,
    input  wire [31:0] imem_rdata,
    output wire [31:0] dmem_addr,
    output wire [31:0] dmem_wdata,
    input  wire [31:0] dmem_rdata,
    output wire        dmem_we
);

    reg  [31:0] pc_reg;
    wire [31:0] pc_next;
    wire [31:0] pc_plus_4        = pc_reg + 32'd4;
    wire [31:0] pc_branch_target;
    assign imem_addr             = pc_reg;

    always @(posedge clk or posedge reset) begin
        if (reset) pc_reg <= 32'h00000000;
        else       pc_reg <= pc_next;
    end

    wire [31:0] instr  = imem_rdata;
    wire [6:0]  opcode = instr[6:0];
    wire [4:0]  rd     = instr[11:7];
    wire [2:0]  funct3 = instr[14:12];
    wire [4:0]  rs1    = instr[19:15];
    wire [4:0]  rs2    = instr[24:20];
    wire [6:0]  funct7 = instr[31:25];

    wire [31:0] imm_i = {{20{instr[31]}}, instr[31:20]};
    wire [31:0] imm_s = {{20{instr[31]}}, instr[31:25], instr[11:7]};
    wire [31:0] imm_b = {{19{instr[31]}}, instr[31], instr[7], instr[30:25], instr[11:8], 1'b0};

    reg reg_write, alu_src, mem_to_reg, mem_write, branch;
    reg [3:0] alu_control;

    always @(*) begin
        reg_write = 0; alu_src = 0; mem_to_reg = 0; mem_write = 0;
        branch = 0; alu_control = 4'b0000;

        case (opcode)
            7'b0110011: begin // R-type
                reg_write = 1;
                case (funct3)
                    3'b000: alu_control = funct7[5] ? 4'b0001 : 4'b0000; // SUB : ADD
                    3'b001: alu_control = 4'b0010; // SLL
                    3'b110: alu_control = 4'b1000; // OR
                    3'b111: alu_control = 4'b1001; // AND
                    default: alu_control = 4'b0000;
                endcase
            end
            7'b0010011: begin // I-type
                reg_write = 1; alu_src = 1;
                case (funct3)
                    3'b000: alu_control = 4'b0000; // ADDI
                    3'b110: alu_control = 4'b1000; // ORI
                    3'b111: alu_control = 4'b1001; // ANDI
                    default: alu_control = 4'b0000;
                endcase
            end
            7'b0000011: begin // LW
                reg_write = 1; alu_src = 1; mem_to_reg = 1; alu_control = 4'b0000;
            end
            7'b0100011: begin // SW
                mem_write = 1; alu_src = 1; alu_control = 4'b0000;
            end
            7'b1100011: begin // BEQ
                branch = 1; alu_control = 4'b0001;
            end
            default: ;
        endcase
    end
    assign dmem_we = mem_write;

    reg [31:0] registers [0:31];
    wire [31:0] rf_rdata1 = (rs1 == 0) ? 32'd0 : registers[rs1];
    wire [31:0] rf_rdata2 = (rs2 == 0) ? 32'd0 : registers[rs2];
    wire [31:0] rf_wdata;

    integer i;
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            for (i = 0; i < 32; i = i + 1) registers[i] <= 32'd0;
        end else if (reg_write && (rd != 0)) begin
            registers[rd] <= rf_wdata;
        end
    end

    wire [31:0] alu_in1 = rf_rdata1;
    wire [31:0] alu_in2 = (alu_src) ? ((opcode == 7'b0100011) ? imm_s : imm_i) : rf_rdata2;
    reg  [31:0] alu_out;
    wire        alu_zero = (alu_out == 32'd0);

    always @(*) begin
        case (alu_control)
            4'b0000: alu_out = alu_in1 + alu_in2; // ADD
            4'b0001: alu_out = alu_in1 - alu_in2; // SUB
            4'b0010: alu_out = alu_in1 << alu_in2[4:0]; // SLL
            4'b1000: alu_out = alu_in1 | alu_in2; // OR
            4'b1001: alu_out = alu_in1 & alu_in2; // AND
            default: alu_out = 32'd0;
        endcase
    end

    assign dmem_addr  = alu_out;
    assign dmem_wdata = rf_rdata2;
    assign rf_wdata   = (mem_to_reg) ? dmem_rdata : alu_out;

    wire take_branch = branch && alu_zero;
    assign pc_branch_target = pc_reg + imm_b;
    assign pc_next = take_branch ? pc_branch_target : pc_plus_4;

endmodule
