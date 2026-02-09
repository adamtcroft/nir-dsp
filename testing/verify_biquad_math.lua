#!/usr/bin/env lua
--[[
    Biquad Filter Mathematical Verification
    
    Verifies that biquad filter coefficients are calculated correctly by
    computing the expected frequency response analytically.
    
    No external dependencies - pure Lua math.
    
    Usage: lua verify_biquad_math.lua
    
    (C) 2026 NIR, LLC - All Rights Reserved
]]

local pi = math.pi

-- Complex number operations (Lua doesn't have native complex support)
local Complex = {}
Complex.__index = Complex

function Complex.new(real, imag)
    return setmetatable({real = real or 0, imag = imag or 0}, Complex)
end

function Complex:__add(other)
    return Complex.new(self.real + other.real, self.imag + other.imag)
end

function Complex:__sub(other)
    return Complex.new(self.real - other.real, self.imag - other.imag)
end

function Complex:__mul(other)
    return Complex.new(
        self.real * other.real - self.imag * other.imag,
        self.real * other.imag + self.imag * other.real
    )
end

function Complex:__div(other)
    local denom = other.real * other.real + other.imag * other.imag
    return Complex.new(
        (self.real * other.real + self.imag * other.imag) / denom,
        (self.imag * other.real - self.real * other.imag) / denom
    )
end

function Complex:magnitude()
    return math.sqrt(self.real * self.real + self.imag * self.imag)
end

function Complex:phase()
    return math.atan2(self.imag, self.real)
end

-- Calculate e^(j*theta) = cos(theta) + j*sin(theta)
function Complex.exp_j(theta)
    return Complex.new(math.cos(theta), math.sin(theta))
end


-- Biquad coefficient calculation (RBJ cookbook formulas)
local function calc_lowpass_coeffs(cutoff, q, sample_rate)
    local omega = 2 * pi * cutoff / sample_rate
    local sin_omega = math.sin(omega)
    local cos_omega = math.cos(omega)
    local alpha = sin_omega / (2 * q)
    
    local a0 = 1 + alpha
    local b0 = ((1 - cos_omega) / 2) / a0
    local b1 = (1 - cos_omega) / a0
    local b2 = ((1 - cos_omega) / 2) / a0
    local a1 = (-2 * cos_omega) / a0
    local a2 = (1 - alpha) / a0
    
    return {b0 = b0, b1 = b1, b2 = b2, a1 = a1, a2 = a2}
end

local function calc_highpass_coeffs(cutoff, q, sample_rate)
    local omega = 2 * pi * cutoff / sample_rate
    local sin_omega = math.sin(omega)
    local cos_omega = math.cos(omega)
    local alpha = sin_omega / (2 * q)
    
    local a0 = 1 + alpha
    local b0 = ((1 + cos_omega) / 2) / a0
    local b1 = (-(1 + cos_omega)) / a0
    local b2 = ((1 + cos_omega) / 2) / a0
    local a1 = (-2 * cos_omega) / a0
    local a2 = (1 - alpha) / a0
    
    return {b0 = b0, b1 = b1, b2 = b2, a1 = a1, a2 = a2}
end


-- Calculate frequency response H(f) for given coefficients
-- H(z) = (b0 + b1*z^-1 + b2*z^-2) / (1 + a1*z^-1 + a2*z^-2)
-- where z = e^(j*2*pi*f/fs)
local function frequency_response(coeffs, freq, sample_rate)
    local omega = 2 * pi * freq / sample_rate
    local z = Complex.exp_j(omega)
    local z_inv = Complex.new(1, 0) / z
    local z_inv2 = z_inv * z_inv
    
    -- Numerator: b0 + b1*z^-1 + b2*z^-2
    local num = Complex.new(coeffs.b0, 0) + 
                Complex.new(coeffs.b1, 0) * z_inv + 
                Complex.new(coeffs.b2, 0) * z_inv2
    
    -- Denominator: 1 + a1*z^-1 + a2*z^-2
    local den = Complex.new(1, 0) + 
                Complex.new(coeffs.a1, 0) * z_inv + 
                Complex.new(coeffs.a2, 0) * z_inv2
    
    return num / den
end


-- Convert linear magnitude to dB
local function linear_to_db(linear)
    if linear <= 0 then return -math.huge end
    return 20 * math.log10(linear)
end


-- Test helpers
local function test_header(name)
    print(string.rep("=", 60))
    print(name)
    print(string.rep("=", 60))
end

local function test_result(passed, message)
    local status = passed and "PASS" or "FAIL"
    print(string.format("  [%s] %s", status, message))
    return passed
end


-- Verify low-pass filter
local function verify_lowpass(cutoff, q, sample_rate)
    test_header(string.format("Low-Pass Filter: fc=%dHz, Q=%.3f, fs=%dHz", cutoff, q, sample_rate))
    
    local coeffs = calc_lowpass_coeffs(cutoff, q, sample_rate)
    local all_passed = true
    
    -- Print coefficients
    print(string.format("  Coefficients: b0=%.6f, b1=%.6f, b2=%.6f", coeffs.b0, coeffs.b1, coeffs.b2))
    print(string.format("                a1=%.6f, a2=%.6f", coeffs.a1, coeffs.a2))
    print()
    
    -- Test 1: DC response should be 0dB (unity gain at 0Hz)
    local dc_response = frequency_response(coeffs, 1, sample_rate)
    local dc_db = linear_to_db(dc_response:magnitude())
    all_passed = test_result(math.abs(dc_db) < 0.1, 
        string.format("DC response: %.2f dB (expected: ~0 dB)", dc_db)) and all_passed
    
    -- Test 2: Response at cutoff should be ~-3dB (for Butterworth Q=0.707)
    local cutoff_response = frequency_response(coeffs, cutoff, sample_rate)
    local cutoff_db = linear_to_db(cutoff_response:magnitude())
    local expected_cutoff_db = (q == 0.707) and -3.01 or nil
    if expected_cutoff_db then
        all_passed = test_result(math.abs(cutoff_db - expected_cutoff_db) < 0.5,
            string.format("Cutoff response: %.2f dB (expected: ~%.2f dB)", cutoff_db, expected_cutoff_db)) and all_passed
    else
        print(string.format("  [INFO] Cutoff response: %.2f dB (Q=%.3f, not Butterworth)", cutoff_db, q))
    end
    
    -- Test 3: Response at 2x cutoff should show rolloff
    local octave_up = frequency_response(coeffs, cutoff * 2, sample_rate)
    local octave_up_db = linear_to_db(octave_up:magnitude())
    -- For a 2-pole filter, expect ~-12dB/octave, so -12dB from cutoff at 2x
    local expected_rolloff = cutoff_db - 12
    all_passed = test_result(octave_up_db < cutoff_db - 6,
        string.format("1 octave above cutoff: %.2f dB (expected: <%.2f dB)", octave_up_db, cutoff_db - 6)) and all_passed
    
    -- Test 4: Response at 4x cutoff (2 octaves up)
    if cutoff * 4 < sample_rate / 2 then
        local two_oct_up = frequency_response(coeffs, cutoff * 4, sample_rate)
        local two_oct_db = linear_to_db(two_oct_up:magnitude())
        all_passed = test_result(two_oct_db < cutoff_db - 18,
            string.format("2 octaves above cutoff: %.2f dB (expected: <%.2f dB)", two_oct_db, cutoff_db - 18)) and all_passed
    end
    
    -- Print frequency response table
    print()
    print("  Frequency Response:")
    print(string.format("  %10s | %10s", "Freq (Hz)", "Gain (dB)"))
    print("  " .. string.rep("-", 25))
    
    local test_freqs = {20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000}
    for _, freq in ipairs(test_freqs) do
        if freq < sample_rate / 2 then
            local response = frequency_response(coeffs, freq, sample_rate)
            local db = linear_to_db(response:magnitude())
            local marker = (freq == cutoff) and " <-- cutoff" or ""
            print(string.format("  %10d | %+10.2f%s", freq, db, marker))
        end
    end
    
    print()
    return all_passed
end


-- Verify high-pass filter
local function verify_highpass(cutoff, q, sample_rate)
    test_header(string.format("High-Pass Filter: fc=%dHz, Q=%.3f, fs=%dHz", cutoff, q, sample_rate))
    
    local coeffs = calc_highpass_coeffs(cutoff, q, sample_rate)
    local all_passed = true
    
    -- Print coefficients
    print(string.format("  Coefficients: b0=%.6f, b1=%.6f, b2=%.6f", coeffs.b0, coeffs.b1, coeffs.b2))
    print(string.format("                a1=%.6f, a2=%.6f", coeffs.a1, coeffs.a2))
    print()
    
    -- Test 1: High frequency response should be ~0dB
    local hf_response = frequency_response(coeffs, sample_rate / 4, sample_rate)
    local hf_db = linear_to_db(hf_response:magnitude())
    all_passed = test_result(math.abs(hf_db) < 1,
        string.format("High freq response (fs/4): %.2f dB (expected: ~0 dB)", hf_db)) and all_passed
    
    -- Test 2: Response at cutoff should be ~-3dB (for Butterworth Q=0.707)
    local cutoff_response = frequency_response(coeffs, cutoff, sample_rate)
    local cutoff_db = linear_to_db(cutoff_response:magnitude())
    local expected_cutoff_db = (q == 0.707) and -3.01 or nil
    if expected_cutoff_db then
        all_passed = test_result(math.abs(cutoff_db - expected_cutoff_db) < 0.5,
            string.format("Cutoff response: %.2f dB (expected: ~%.2f dB)", cutoff_db, expected_cutoff_db)) and all_passed
    else
        print(string.format("  [INFO] Cutoff response: %.2f dB (Q=%.3f, not Butterworth)", cutoff_db, q))
    end
    
    -- Test 3: Response at cutoff/2 should show rolloff
    local octave_down = frequency_response(coeffs, cutoff / 2, sample_rate)
    local octave_down_db = linear_to_db(octave_down:magnitude())
    all_passed = test_result(octave_down_db < cutoff_db - 6,
        string.format("1 octave below cutoff: %.2f dB (expected: <%.2f dB)", octave_down_db, cutoff_db - 6)) and all_passed
    
    -- Test 4: Response at cutoff/4 (2 octaves down)
    if cutoff / 4 > 10 then
        local two_oct_down = frequency_response(coeffs, cutoff / 4, sample_rate)
        local two_oct_db = linear_to_db(two_oct_down:magnitude())
        all_passed = test_result(two_oct_db < cutoff_db - 18,
            string.format("2 octaves below cutoff: %.2f dB (expected: <%.2f dB)", two_oct_db, cutoff_db - 18)) and all_passed
    end
    
    -- Print frequency response table
    print()
    print("  Frequency Response:")
    print(string.format("  %10s | %10s", "Freq (Hz)", "Gain (dB)"))
    print("  " .. string.rep("-", 25))
    
    local test_freqs = {20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000}
    for _, freq in ipairs(test_freqs) do
        if freq < sample_rate / 2 then
            local response = frequency_response(coeffs, freq, sample_rate)
            local db = linear_to_db(response:magnitude())
            local marker = (freq == cutoff) and " <-- cutoff" or ""
            print(string.format("  %10d | %+10.2f%s", freq, db, marker))
        end
    end
    
    print()
    return all_passed
end


-- Main test runner
local function run_tests()
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       Biquad Filter Mathematical Verification            ║")
    print("║       Pure Lua - No External Dependencies                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    local all_passed = true
    local sample_rate = 48000
    
    -- Test low-pass filters
    all_passed = verify_lowpass(1000, 0.707, sample_rate) and all_passed
    all_passed = verify_lowpass(500, 0.707, sample_rate) and all_passed
    all_passed = verify_lowpass(5000, 0.707, sample_rate) and all_passed
    
    -- Test with different Q values
    all_passed = verify_lowpass(1000, 0.5, sample_rate) and all_passed
    all_passed = verify_lowpass(1000, 2.0, sample_rate) and all_passed
    
    -- Test high-pass filters
    all_passed = verify_highpass(1000, 0.707, sample_rate) and all_passed
    all_passed = verify_highpass(200, 0.707, sample_rate) and all_passed
    
    -- Summary
    print(string.rep("=", 60))
    if all_passed then
        print("ALL TESTS PASSED!")
    else
        print("SOME TESTS FAILED - Review output above")
    end
    print(string.rep("=", 60))
    
    return all_passed
end


-- Run if executed directly
if arg and arg[0]:match("verify_biquad_math%.lua$") then
    local success = run_tests()
    os.exit(success and 0 or 1)
end


-- Export for use as module
return {
    calc_lowpass_coeffs = calc_lowpass_coeffs,
    calc_highpass_coeffs = calc_highpass_coeffs,
    frequency_response = frequency_response,
    linear_to_db = linear_to_db,
    verify_lowpass = verify_lowpass,
    verify_highpass = verify_highpass,
    Complex = Complex
}
