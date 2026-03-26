// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop__Syms.h"
#include "Vtop___024root.h"

// Parameter definitions for Vtop___024root
constexpr CData/*2:0*/ Vtop___024root::periph_ctrl__DOT__ADDR_ID;
constexpr CData/*2:0*/ Vtop___024root::periph_ctrl__DOT__ADDR_GPIO;
constexpr CData/*2:0*/ Vtop___024root::periph_ctrl__DOT__ADDR_CTRL;
constexpr CData/*2:0*/ Vtop___024root::periph_ctrl__DOT__ADDR_STATUS;
constexpr CData/*7:0*/ Vtop___024root::periph_ctrl__DOT__PERIPHERAL_ID;


void Vtop___024root___ctor_var_reset(Vtop___024root* vlSelf);

Vtop___024root::Vtop___024root(Vtop__Syms* symsp, const char* v__name)
    : VerilatedModule{v__name}
    , vlSymsp{symsp}
 {
    // Reset structure values
    Vtop___024root___ctor_var_reset(this);
}

void Vtop___024root::__Vconfigure(bool first) {
    (void)first;  // Prevent unused variable warning
}

Vtop___024root::~Vtop___024root() {
}
