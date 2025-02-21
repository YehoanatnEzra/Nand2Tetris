// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

@R14
D=M
@min
M=D
@max
M=D
@i
M=0

(LOOP)
@R15
D=M
@i
D=D-M
@STOP
D;JEQ

// Check if arr[i] < min
@R14
D=M
@i
D=D+M
A=D
D=M
@min
A=M
D=D-M
@changeWithMin
D;JLT

// Check if arr[i] > max
@R14
D=M
@i
D=D+M
A=D
D=M
@max
A=M
D=D-M
@changeWithMax
D;JGT

@i
M=M+1
@LOOP
0;JMP

(changeWithMin)
@R14
D=M
@i
D=D+M
@min
M=D
@i
M=M+1
@LOOP
0;JMP

(changeWithMax)
@R14
D=M
@i
D=D+M
@max
M=D
@i
M=M+1
@LOOP
0;JMP

(STOP)
//temp=min
@min
A=M
D=M
@temp
M=D

//min=max
@max
A=M
D=M
@min
M=D

//max=temp(min)
@temp
D=M
@max
A=M
M=D

(END)
@END
0;JMP