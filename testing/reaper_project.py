#!/usr/bin/env python3
"""
REAPER project file (.rpp) generator for JSFX testing.
Creates minimal project files with test signals and JSFX effects loaded.
"""

from pathlib import Path
from typing import Dict, List, Optional


class ReaperProject:
    """Generate REAPER project files for automated testing."""
    
    def __init__(self, sample_rate=48000, bpm=120):
        """
        Initialize REAPER project generator.
        
        Args:
            sample_rate: Project sample rate
            bpm: Project tempo (BPM)
        """
        self.sample_rate = sample_rate
        self.bpm = bpm
        self.tracks = []
        
    def add_track_with_media(self, media_file, track_name="Test", jsfx_effects=None):
        """
        Add a track with media file and optional JSFX effects.
        
        Args:
            media_file: Path to audio file (WAV)
            track_name: Name of the track
            jsfx_effects: List of tuples (jsfx_path, slider_values_dict)
                         Example: [("LowPassFilter.jsfx", {"frequencySlider": 1000})]
        """
        track = {
            'name': track_name,
            'media_file': str(Path(media_file).absolute()),
            'effects': jsfx_effects or []
        }
        self.tracks.append(track)
        
    def _format_fx_chain(self, effects):
        """Format FX chain for .rpp file."""
        if not effects:
            return ""
        
        fx_lines = ["  <FXCHAIN"]
        
        for idx, (jsfx_path, sliders) in enumerate(effects):
            jsfx_name = Path(jsfx_path).stem
            fx_lines.append(f"    WNDRECT 0 0 0 0")
            fx_lines.append(f"    SHOW 0")
            fx_lines.append(f"    LASTSEL 0")
            fx_lines.append(f"    DOCKED 0")
            fx_lines.append(f"    <JS {jsfx_name} \"{jsfx_path}\"")
            
            # Add slider values
            slider_count = len(sliders) if sliders else 0
            slider_line = f"    {slider_count}"
            
            if sliders:
                # JSFX sliders are indexed starting from 1
                for slider_name, value in sliders.items():
                    slider_line += f" {value}"
            
            fx_lines.append(slider_line)
            fx_lines.append(f"    >")
        
        fx_lines.append("  >")
        return "\n".join(fx_lines)
    
    def generate_rpp(self, output_file, render_settings=None):
        """
        Generate .rpp project file.
        
        Args:
            output_file: Output .rpp filename
            render_settings: Optional dict with render settings
                           Keys: 'tail_ms' (render tail in ms, default 1000)
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        render_settings = render_settings or {}
        tail_ms = render_settings.get('tail_ms', 1000)
        
        # Build project content
        lines = [
            "<REAPER_PROJECT 0.1 \"7.0\" 1234567890",
            f"  SAMPLERATE {self.sample_rate} 0 0",
            f"  TEMPO {self.bpm} 4 4",
            "  MASTERAUTOMODE 0",
            "  MASTERVUMODE 0",
            "  MASTERTRACKHEIGHT 0",
            "  MASTERPEAKCOL 16576",
            "  RECORD_PATH \"\" \"\"",
            f"  RENDER_FILE \"\"",
            f"  RENDER_PATTERN \"\"",
            f"  RENDER_FMT 0 2 {self.sample_rate}",  # WAV, 16-bit, sample rate
            f"  RENDER_1X 0",
            f"  RENDER_RANGE 1 0 0 18 1000",  # Render project, time selection
            f"  RENDER_RESAMPLE 3 0 1",
            f"  RENDER_ADDTOPROJ 0",
            f"  RENDER_STEMS 0",
            f"  RENDER_DITHER 0",
            f"  TIMELOCKMODE 1",
            f"  RENDER_TAILFLAG 1",
            f"  RENDER_TAILMS {tail_ms}",
        ]
        
        # Add tracks
        for track_idx, track in enumerate(self.tracks):
            lines.append(f"  <TRACK {{{'{'}{track_idx:08X}-0000-0000-0000-000000000000'}}}")
            lines.append(f"    NAME \"{track['name']}\"")
            lines.append(f"    PEAKCOL 16576")
            lines.append(f"    VOLPAN 1 0 -1 -1 1")
            lines.append(f"    MUTESOLO 0 0 0")
            lines.append(f"    IPHASE 0")
            lines.append(f"    PLAYOFFS 0 1")
            lines.append(f"    ISBUS 0 0")
            lines.append(f"    BUSCOMP 0 0 0 0 0")
            lines.append(f"    SHOWINMIX 1 0.6667 0.5 1 0.5 0 0 0")
            lines.append(f"    SEL 0")
            lines.append(f"    REC 0 0 1 0 0 0 0 0")
            lines.append(f"    VU 2")
            lines.append(f"    TRACKHEIGHT 0 0 0 0 0 0")
            lines.append(f"    INQ 0 0 0 0.5 100 0 0 100")
            lines.append(f"    NCHAN 2")
            
            # Add FX chain
            fx_chain = self._format_fx_chain(track['effects'])
            if fx_chain:
                lines.append(fx_chain)
            
            # Add media item
            media_path = track['media_file']
            lines.append(f"    <ITEM")
            lines.append(f"      POSITION 0")
            lines.append(f"      LENGTH 10")  # Length will be auto-adjusted
            lines.append(f"      LOOP 0")
            lines.append(f"      ALLTAKES 0")
            lines.append(f"      FADEIN 1 0 0 1 0 0 0")
            lines.append(f"      FADEOUT 1 0 0 1 0 0 0")
            lines.append(f"      VOLPAN 1 0 1 -1")
            lines.append(f"      <SOURCE WAVE")
            lines.append(f"        FILE \"{media_path}\"")
            lines.append(f"      >")
            lines.append(f"    >")
            
            lines.append(f"  >")
        
        lines.append(">")
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return output_path


def create_test_project(jsfx_path, input_wav, output_rpp, slider_values=None, sample_rate=48000):
    """
    Quick helper to create a test project.
    
    Args:
        jsfx_path: Path to JSFX effect file
        input_wav: Path to input WAV file
        output_rpp: Path for output .rpp file
        slider_values: Dict of slider values (e.g., {"frequencySlider": 1000})
        sample_rate: Project sample rate
    
    Returns:
        Path to created .rpp file
    """
    project = ReaperProject(sample_rate=sample_rate)
    project.add_track_with_media(
        media_file=input_wav,
        track_name="Test Signal",
        jsfx_effects=[(jsfx_path, slider_values or {})]
    )
    return project.generate_rpp(output_rpp)


if __name__ == "__main__":
    # Example usage
    create_test_project(
        jsfx_path="LowPassFilter.jsfx",
        input_wav="test_signals/sine_1000hz.wav",
        output_rpp="test_projects/test_lowpass.rpp",
        slider_values={"frequencySlider": 500}
    )
    print("Created test project: test_projects/test_lowpass.rpp")
