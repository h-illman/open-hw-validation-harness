// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vtop__Syms.h"


void Vtop___024root__trace_chg_0_sub_0(Vtop___024root* vlSelf, VerilatedVcd::Buffer* bufp);

void Vtop___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_chg_0\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (VL_UNLIKELY(!vlSymsp->__Vm_activity)) return;
    // Body
    Vtop___024root__trace_chg_0_sub_0((&vlSymsp->TOP), bufp);
}

void Vtop___024root__trace_chg_0_sub_0(Vtop___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_chg_0_sub_0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode + 1);
    // Body
    bufp->chgBit(oldp+0,(vlSelfRef.clk));
    bufp->chgBit(oldp+1,(vlSelfRef.rst_n));
    bufp->chgCData(oldp+2,(vlSelfRef.addr),3);
    bufp->chgBit(oldp+3,(vlSelfRef.wr_en));
    bufp->chgBit(oldp+4,(vlSelfRef.rd_en));
    bufp->chgCData(oldp+5,(vlSelfRef.wr_data),8);
    bufp->chgCData(oldp+6,(vlSelfRef.rd_data),8);
    bufp->chgBit(oldp+7,(vlSelfRef.rd_valid));
    bufp->chgBit(oldp+8,(vlSelfRef.addr_err));
    bufp->chgCData(oldp+9,(vlSelfRef.gpio_out),8);
    bufp->chgBit(oldp+10,(vlSelfRef.periph_ctrl__DOT__clk));
    bufp->chgBit(oldp+11,(vlSelfRef.periph_ctrl__DOT__rst_n));
    bufp->chgCData(oldp+12,(vlSelfRef.periph_ctrl__DOT__addr),3);
    bufp->chgBit(oldp+13,(vlSelfRef.periph_ctrl__DOT__wr_en));
    bufp->chgBit(oldp+14,(vlSelfRef.periph_ctrl__DOT__rd_en));
    bufp->chgCData(oldp+15,(vlSelfRef.periph_ctrl__DOT__wr_data),8);
    bufp->chgCData(oldp+16,(vlSelfRef.periph_ctrl__DOT__rd_data),8);
    bufp->chgBit(oldp+17,(vlSelfRef.periph_ctrl__DOT__rd_valid));
    bufp->chgBit(oldp+18,(vlSelfRef.periph_ctrl__DOT__addr_err));
    bufp->chgCData(oldp+19,(vlSelfRef.periph_ctrl__DOT__gpio_out),8);
    bufp->chgCData(oldp+20,(vlSelfRef.periph_ctrl__DOT__reg_gpio),8);
    bufp->chgCData(oldp+21,(vlSelfRef.periph_ctrl__DOT__reg_ctrl),8);
    bufp->chgBit(oldp+22,(vlSelfRef.periph_ctrl__DOT__addr_valid));
    bufp->chgCData(oldp+23,(vlSelfRef.periph_ctrl__DOT__reg_status),8);
}

void Vtop___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root__trace_cleanup\n"); );
    // Init
    Vtop___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vtop___024root*>(voidSelf);
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VlUnpacked<CData/*0:0*/, 1> __Vm_traceActivity;
    for (int __Vi0 = 0; __Vi0 < 1; ++__Vi0) {
        __Vm_traceActivity[__Vi0] = 0;
    }
    // Body
    vlSymsp->__Vm_activity = false;
    __Vm_traceActivity[0U] = 0U;
}
