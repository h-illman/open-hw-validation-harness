// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vtop.h for the primary calling header

#ifndef VERILATED_VTOP___024ROOT_H_
#define VERILATED_VTOP___024ROOT_H_  // guard

#include "verilated.h"


class Vtop__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vtop___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    VL_IN8(clk,0,0);
    VL_IN8(rst_n,0,0);
    VL_IN8(addr,2,0);
    VL_IN8(wr_en,0,0);
    VL_IN8(rd_en,0,0);
    VL_IN8(wr_data,7,0);
    VL_OUT8(rd_data,7,0);
    VL_OUT8(rd_valid,0,0);
    VL_OUT8(addr_err,0,0);
    VL_OUT8(gpio_out,7,0);
    CData/*0:0*/ periph_ctrl__DOT__clk;
    CData/*0:0*/ periph_ctrl__DOT__rst_n;
    CData/*2:0*/ periph_ctrl__DOT__addr;
    CData/*0:0*/ periph_ctrl__DOT__wr_en;
    CData/*0:0*/ periph_ctrl__DOT__rd_en;
    CData/*7:0*/ periph_ctrl__DOT__wr_data;
    CData/*7:0*/ periph_ctrl__DOT__rd_data;
    CData/*0:0*/ periph_ctrl__DOT__rd_valid;
    CData/*0:0*/ periph_ctrl__DOT__addr_err;
    CData/*7:0*/ periph_ctrl__DOT__gpio_out;
    CData/*7:0*/ periph_ctrl__DOT__reg_gpio;
    CData/*7:0*/ periph_ctrl__DOT__reg_ctrl;
    CData/*0:0*/ periph_ctrl__DOT__addr_valid;
    CData/*7:0*/ periph_ctrl__DOT__reg_status;
    CData/*0:0*/ __VstlFirstIteration;
    CData/*0:0*/ __VicoFirstIteration;
    CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
    CData/*0:0*/ __VactContinue;
    IData/*31:0*/ __VactIterCount;
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<1> __VactTriggered;
    VlTriggerVec<1> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vtop__Syms* const vlSymsp;

    // PARAMETERS
    static constexpr CData/*2:0*/ periph_ctrl__DOT__ADDR_ID = 0U;
    static constexpr CData/*2:0*/ periph_ctrl__DOT__ADDR_GPIO = 1U;
    static constexpr CData/*2:0*/ periph_ctrl__DOT__ADDR_CTRL = 2U;
    static constexpr CData/*2:0*/ periph_ctrl__DOT__ADDR_STATUS = 3U;
    static constexpr CData/*7:0*/ periph_ctrl__DOT__PERIPHERAL_ID = 0xabU;

    // CONSTRUCTORS
    Vtop___024root(Vtop__Syms* symsp, const char* v__name);
    ~Vtop___024root();
    VL_UNCOPYABLE(Vtop___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
