// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop___024root.h"

void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VicoTriggered.word(0U))) {
        Vtop___024root___ico_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtop___024root___ico_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___ico_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.periph_ctrl__DOT__clk = vlSelfRef.clk;
    vlSelfRef.periph_ctrl__DOT__rst_n = vlSelfRef.rst_n;
    vlSelfRef.periph_ctrl__DOT__addr = vlSelfRef.addr;
    vlSelfRef.periph_ctrl__DOT__wr_en = vlSelfRef.wr_en;
    vlSelfRef.periph_ctrl__DOT__rd_en = vlSelfRef.rd_en;
    vlSelfRef.periph_ctrl__DOT__wr_data = vlSelfRef.wr_data;
    vlSelfRef.periph_ctrl__DOT__addr_valid = (3U >= (IData)(vlSelfRef.addr));
    vlSelfRef.rd_data = vlSelfRef.periph_ctrl__DOT__rd_data;
    vlSelfRef.rd_valid = vlSelfRef.periph_ctrl__DOT__rd_valid;
    vlSelfRef.addr_err = vlSelfRef.periph_ctrl__DOT__addr_err;
    vlSelfRef.gpio_out = vlSelfRef.periph_ctrl__DOT__reg_gpio;
    vlSelfRef.periph_ctrl__DOT__gpio_out = vlSelfRef.periph_ctrl__DOT__reg_gpio;
    vlSelfRef.periph_ctrl__DOT__reg_status = ((2U & 
                                               ((IData)(vlSelfRef.periph_ctrl__DOT__reg_ctrl) 
                                                << 1U)) 
                                              | (0U 
                                                 != (IData)(vlSelfRef.periph_ctrl__DOT__reg_gpio)));
}

void Vtop___024root___eval_triggers__ico(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__ico(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__ico\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VicoExecute;
    // Body
    Vtop___024root___eval_triggers__ico(vlSelf);
    __VicoExecute = vlSelfRef.__VicoTriggered.any();
    if (__VicoExecute) {
        Vtop___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vtop___024root___eval_act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
}

void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf);

void Vtop___024root___eval_nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if ((1ULL & vlSelfRef.__VnbaTriggered.word(0U))) {
        Vtop___024root___nba_sequent__TOP__0(vlSelf);
    }
}

VL_INLINE_OPT void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___nba_sequent__TOP__0\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.rst_n) {
        vlSelfRef.periph_ctrl__DOT__rd_valid = 0U;
        vlSelfRef.periph_ctrl__DOT__addr_err = 0U;
        if (((IData)(vlSelfRef.rd_en) | (IData)(vlSelfRef.wr_en))) {
            if (vlSelfRef.periph_ctrl__DOT__addr_valid) {
                if (vlSelfRef.rd_en) {
                    vlSelfRef.periph_ctrl__DOT__rd_valid = 1U;
                    vlSelfRef.periph_ctrl__DOT__rd_data 
                        = ((4U & (IData)(vlSelfRef.addr))
                            ? 0xffU : ((2U & (IData)(vlSelfRef.addr))
                                        ? ((1U & (IData)(vlSelfRef.addr))
                                            ? (IData)(vlSelfRef.periph_ctrl__DOT__reg_status)
                                            : (IData)(vlSelfRef.periph_ctrl__DOT__reg_ctrl))
                                        : ((1U & (IData)(vlSelfRef.addr))
                                            ? (IData)(vlSelfRef.periph_ctrl__DOT__reg_gpio)
                                            : 0xabU)));
                }
            }
            if ((1U & (~ (IData)(vlSelfRef.periph_ctrl__DOT__addr_valid)))) {
                vlSelfRef.periph_ctrl__DOT__addr_err = 1U;
            }
        }
        if (((IData)(vlSelfRef.wr_en) & (IData)(vlSelfRef.periph_ctrl__DOT__addr_valid))) {
            if ((1U != (IData)(vlSelfRef.addr))) {
                if ((2U == (IData)(vlSelfRef.addr))) {
                    vlSelfRef.periph_ctrl__DOT__reg_ctrl 
                        = vlSelfRef.wr_data;
                }
            }
            if ((1U == (IData)(vlSelfRef.addr))) {
                vlSelfRef.periph_ctrl__DOT__reg_gpio 
                    = vlSelfRef.wr_data;
            }
        }
    } else {
        vlSelfRef.periph_ctrl__DOT__rd_valid = 0U;
        vlSelfRef.periph_ctrl__DOT__addr_err = 0U;
        vlSelfRef.periph_ctrl__DOT__rd_data = 0U;
        vlSelfRef.periph_ctrl__DOT__reg_ctrl = 0U;
        vlSelfRef.periph_ctrl__DOT__reg_gpio = 0U;
    }
    vlSelfRef.rd_valid = vlSelfRef.periph_ctrl__DOT__rd_valid;
    vlSelfRef.addr_err = vlSelfRef.periph_ctrl__DOT__addr_err;
    vlSelfRef.rd_data = vlSelfRef.periph_ctrl__DOT__rd_data;
    vlSelfRef.gpio_out = vlSelfRef.periph_ctrl__DOT__reg_gpio;
    vlSelfRef.periph_ctrl__DOT__gpio_out = vlSelfRef.periph_ctrl__DOT__reg_gpio;
    vlSelfRef.periph_ctrl__DOT__reg_status = ((2U & 
                                               ((IData)(vlSelfRef.periph_ctrl__DOT__reg_ctrl) 
                                                << 1U)) 
                                              | (0U 
                                                 != (IData)(vlSelfRef.periph_ctrl__DOT__reg_gpio)));
}

void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf);

bool Vtop___024root___eval_phase__act(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__act\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    VlTriggerVec<1> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vtop___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelfRef.__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelfRef.__VactTriggered, vlSelfRef.__VnbaTriggered);
        vlSelfRef.__VnbaTriggered.thisOr(vlSelfRef.__VactTriggered);
        Vtop___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vtop___024root___eval_phase__nba(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_phase__nba\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelfRef.__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vtop___024root___eval_nba(vlSelf);
        vlSelfRef.__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__ico(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__nba(Vtop___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Init
    IData/*31:0*/ __VicoIterCount;
    CData/*0:0*/ __VicoContinue;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VicoIterCount = 0U;
    vlSelfRef.__VicoFirstIteration = 1U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        if (VL_UNLIKELY(((0x64U < __VicoIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__ico(vlSelf);
#endif
            VL_FATAL_MT("/mnt/d/CADDesigns/CODING/ActualCode/AntigravityProjects/open-hw-validation-harness/rtl/example_dut/periph_ctrl.v", 34, "", "Input combinational region did not converge.");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        __VicoContinue = 0U;
        if (Vtop___024root___eval_phase__ico(vlSelf)) {
            __VicoContinue = 1U;
        }
        vlSelfRef.__VicoFirstIteration = 0U;
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY(((0x64U < __VnbaIterCount)))) {
#ifdef VL_DEBUG
            Vtop___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("/mnt/d/CADDesigns/CODING/ActualCode/AntigravityProjects/open-hw-validation-harness/rtl/example_dut/periph_ctrl.v", 34, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelfRef.__VactIterCount = 0U;
        vlSelfRef.__VactContinue = 1U;
        while (vlSelfRef.__VactContinue) {
            if (VL_UNLIKELY(((0x64U < vlSelfRef.__VactIterCount)))) {
#ifdef VL_DEBUG
                Vtop___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("/mnt/d/CADDesigns/CODING/ActualCode/AntigravityProjects/open-hw-validation-harness/rtl/example_dut/periph_ctrl.v", 34, "", "Active region did not converge.");
            }
            vlSelfRef.__VactIterCount = ((IData)(1U) 
                                         + vlSelfRef.__VactIterCount);
            vlSelfRef.__VactContinue = 0U;
            if (Vtop___024root___eval_phase__act(vlSelf)) {
                vlSelfRef.__VactContinue = 1U;
            }
        }
        if (Vtop___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vtop___024root___eval_debug_assertions(Vtop___024root* vlSelf) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_debug_assertions\n"); );
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (VL_UNLIKELY(((vlSelfRef.clk & 0xfeU)))) {
        Verilated::overWidthError("clk");}
    if (VL_UNLIKELY(((vlSelfRef.rst_n & 0xfeU)))) {
        Verilated::overWidthError("rst_n");}
    if (VL_UNLIKELY(((vlSelfRef.addr & 0xf8U)))) {
        Verilated::overWidthError("addr");}
    if (VL_UNLIKELY(((vlSelfRef.wr_en & 0xfeU)))) {
        Verilated::overWidthError("wr_en");}
    if (VL_UNLIKELY(((vlSelfRef.rd_en & 0xfeU)))) {
        Verilated::overWidthError("rd_en");}
}
#endif  // VL_DEBUG
