--[[
  REAPER project file (.rpp) generator for JSFX testing.
  Creates minimal project files with test signals and JSFX effects loaded.
  
  Lua port of reaper_project.py
]]

local ReaperProject = {}
ReaperProject.__index = ReaperProject

--- Create a new REAPER project generator
-- @param sample_rate Project sample rate (default 48000)
-- @param bpm Project tempo in BPM (default 120)
-- @return ReaperProject instance
function ReaperProject.new(sample_rate, bpm)
    local self = setmetatable({}, ReaperProject)
    self.sample_rate = sample_rate or 48000
    self.bpm = bpm or 120
    self.tracks = {}
    return self
end

--- Add a track with media file and optional JSFX effects
-- @param media_file Path to audio file (WAV)
-- @param track_name Name of the track (default "Test")
-- @param jsfx_effects Table of effects: {{path, sliders}, {path, sliders}, ...}
--                     sliders is a table of {name = value} pairs
function ReaperProject:add_track_with_media(media_file, track_name, jsfx_effects)
    local track = {
        name = track_name or "Test",
        media_file = media_file,
        effects = jsfx_effects or {}
    }
    table.insert(self.tracks, track)
end

--- Format FX chain for .rpp file
-- @param effects Table of effects
-- @return String containing FX chain section
local function format_fx_chain(effects)
    if not effects or #effects == 0 then
        return ""
    end
    
    local lines = {"  <FXCHAIN"}
    
    for idx, effect in ipairs(effects) do
        local jsfx_path = effect[1]
        local sliders = effect[2] or {}
        
        -- Extract just the filename from path
        local jsfx_name = jsfx_path:match("([^/\\]+)$") or jsfx_path
        jsfx_name = jsfx_name:gsub("%.jsfx$", "")
        
        table.insert(lines, "    WNDRECT 0 0 0 0")
        table.insert(lines, "    SHOW 0")
        table.insert(lines, "    LASTSEL 0")
        table.insert(lines, "    DOCKED 0")
        table.insert(lines, string.format('    <JS %s "%s"', jsfx_name, jsfx_path))
        
        -- Build slider line
        local slider_values = {}
        for name, value in pairs(sliders) do
            table.insert(slider_values, tostring(value))
        end
        
        local slider_count = #slider_values
        local slider_line = "    " .. slider_count
        if slider_count > 0 then
            slider_line = slider_line .. " " .. table.concat(slider_values, " ")
        end
        
        table.insert(lines, slider_line)
        table.insert(lines, "    >")
    end
    
    table.insert(lines, "  >")
    return table.concat(lines, "\n")
end

--- Ensure directory exists for output file
-- @param filepath Path to file
local function ensure_dir(filepath)
    local dir = filepath:match("(.*/)")
    if dir then
        os.execute('mkdir -p "' .. dir .. '"')
    end
end

--- Get absolute path
-- @param path Relative or absolute path
-- @return Absolute path
local function get_absolute_path(path)
    if path:sub(1, 1) == "/" then
        return path
    end
    -- Get current working directory
    local handle = io.popen("pwd")
    if handle then
        local cwd = handle:read("*a"):gsub("%s+$", "")
        handle:close()
        return cwd .. "/" .. path
    end
    return path
end

--- Generate .rpp project file
-- @param output_file Output .rpp filename
-- @param render_settings Optional table with render settings (tail_ms)
-- @return Path to created file
function ReaperProject:generate_rpp(output_file, render_settings)
    ensure_dir(output_file)
    
    render_settings = render_settings or {}
    local tail_ms = render_settings.tail_ms or 1000
    
    local lines = {
        '<REAPER_PROJECT 0.1 "7.0" 1234567890',
        string.format("  SAMPLERATE %d 0 0", self.sample_rate),
        string.format("  TEMPO %d 4 4", self.bpm),
        "  MASTERAUTOMODE 0",
        "  MASTERVUMODE 0",
        "  MASTERTRACKHEIGHT 0",
        "  MASTERPEAKCOL 16576",
        '  RECORD_PATH "" ""',
        '  RENDER_FILE ""',
        '  RENDER_PATTERN ""',
        string.format("  RENDER_FMT 0 2 %d", self.sample_rate),
        "  RENDER_1X 0",
        "  RENDER_RANGE 1 0 0 18 1000",
        "  RENDER_RESAMPLE 3 0 1",
        "  RENDER_ADDTOPROJ 0",
        "  RENDER_STEMS 0",
        "  RENDER_DITHER 0",
        "  TIMELOCKMODE 1",
        "  RENDER_TAILFLAG 1",
        string.format("  RENDER_TAILMS %d", tail_ms),
    }
    
    -- Add tracks
    for track_idx, track in ipairs(self.tracks) do
        local guid = string.format("{%08X-0000-0000-0000-000000000000}", track_idx - 1)
        table.insert(lines, string.format("  <TRACK %s", guid))
        table.insert(lines, string.format('    NAME "%s"', track.name))
        table.insert(lines, "    PEAKCOL 16576")
        table.insert(lines, "    VOLPAN 1 0 -1 -1 1")
        table.insert(lines, "    MUTESOLO 0 0 0")
        table.insert(lines, "    IPHASE 0")
        table.insert(lines, "    PLAYOFFS 0 1")
        table.insert(lines, "    ISBUS 0 0")
        table.insert(lines, "    BUSCOMP 0 0 0 0 0")
        table.insert(lines, "    SHOWINMIX 1 0.6667 0.5 1 0.5 0 0 0")
        table.insert(lines, "    SEL 0")
        table.insert(lines, "    REC 0 0 1 0 0 0 0 0")
        table.insert(lines, "    VU 2")
        table.insert(lines, "    TRACKHEIGHT 0 0 0 0 0 0")
        table.insert(lines, "    INQ 0 0 0 0.5 100 0 0 100")
        table.insert(lines, "    NCHAN 2")
        
        -- Add FX chain
        local fx_chain = format_fx_chain(track.effects)
        if fx_chain ~= "" then
            table.insert(lines, fx_chain)
        end
        
        -- Add media item
        local media_path = get_absolute_path(track.media_file)
        table.insert(lines, "    <ITEM")
        table.insert(lines, "      POSITION 0")
        table.insert(lines, "      LENGTH 10")
        table.insert(lines, "      LOOP 0")
        table.insert(lines, "      ALLTAKES 0")
        table.insert(lines, "      FADEIN 1 0 0 1 0 0 0")
        table.insert(lines, "      FADEOUT 1 0 0 1 0 0 0")
        table.insert(lines, "      VOLPAN 1 0 1 -1")
        table.insert(lines, "      <SOURCE WAVE")
        table.insert(lines, string.format('        FILE "%s"', media_path))
        table.insert(lines, "      >")
        table.insert(lines, "    >")
        
        table.insert(lines, "  >")
    end
    
    table.insert(lines, ">")
    
    -- Write to file
    local file = io.open(output_file, "w")
    if not file then
        error("Could not open file for writing: " .. output_file)
    end
    file:write(table.concat(lines, "\n"))
    file:close()
    
    return output_file
end

--- Quick helper to create a test project
-- @param jsfx_path Path to JSFX effect file
-- @param input_wav Path to input WAV file
-- @param output_rpp Path for output .rpp file
-- @param slider_values Table of slider values
-- @param sample_rate Project sample rate
-- @return Path to created .rpp file
local function create_test_project(jsfx_path, input_wav, output_rpp, slider_values, sample_rate)
    local project = ReaperProject.new(sample_rate or 48000)
    project:add_track_with_media(
        input_wav,
        "Test Signal",
        {{jsfx_path, slider_values or {}}}
    )
    return project:generate_rpp(output_rpp)
end

-- Export module
return {
    ReaperProject = ReaperProject,
    create_test_project = create_test_project
}
