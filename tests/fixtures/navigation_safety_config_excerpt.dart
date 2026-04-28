// Excerpt from aki1770-del/SNGNav navigation_safety_core 0.4.0:
//   packages/navigation_safety_core/lib/src/navigation_safety_config.dart
//   lines 46-80 (DriverProfile.ageingRural and noviceUrban branches).
// Captured 2026-04-28 as a fixture for LiteratureDriftDetectorLoom integration
// test. Refresh by re-pasting from the upstream source if the citation set
// shifts. Source repo: https://github.com/aki1770-del/SNGNav

      case DriverProfile.ageingRural:
        // 0.3.0 calibration corrections per published literature.
        // - infoTemperatureCelsius: 0.2.0 had 5°C; combined with
        //   infoVisibilityMeters 1500m this fired alert-fatigue on
        //   most autumn evenings in Hokkaido/Tohoku (V14 silent
        //   safety failure per arxiv 2410.06388 + AAA-FTS). Lowered
        //   to 4°C to preserve information-tier signal without
        //   firing on routine cold autumn evenings.
        // - warningTemperatureCelsius: 0.2.0 had 1°C; black ice
        //   forms at road-surface ≤0°C even when ambient air is
        //   several degrees warmer (well-documented). 1°C left no
        //   margin above formation envelope. Raised to 2°C.
        return NavigationSafetyConfig(
          safeScoreFloor: 0.85,
          infoScoreFloor: 0.55,
          warningScoreFloor: 0.35,
          infoTemperatureCelsius: 4,
          warningTemperatureCelsius: 2,
          criticalTemperatureCelsius: -3,
          infoVisibilityMeters: 1500,
          warningVisibilityMeters: 300,
          criticalVisibilityMeters: 80,
        );
      case DriverProfile.snowZoneExperienced:
        // Standard defaults. The loom trusts the experienced
        // snow-zone driver's interpretation of standard warnings.
        return NavigationSafetyConfig();
      case DriverProfile.noviceUrban:
        // 0.3.0 calibration correction per published literature.
        // - warningVisibilityMeters: 0.2.0 had 250m (+50m over
        //   standard). Novice hazard-perception RT is 3.58s vs 1.32s
        //   experienced (PubMed 16313881). At 60 km/h that's ~37m
        //   additional reaction-distance from RT alone — +50m left
        //   no braking margin. Raised to 320m to give RT-margin +
        //   braking margin per published novice-fog crash-rate
        //   elevation (Konstantopoulos PubMed 22664714).
