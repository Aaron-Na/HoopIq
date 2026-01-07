package com.hoopiq.api.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;

@RestController
@RequestMapping("/api/schedule")
@CrossOrigin(origins = "*")
public class ScheduleController {

    private final ObjectMapper objectMapper;
    private final Path dataDir;

    public ScheduleController() {
        this.objectMapper = new ObjectMapper();
        // Get the path to the data directory relative to the backend
        String projectRoot = System.getProperty("user.dir");
        // Navigate from backend to nba-zone/data
        this.dataDir = Paths.get(projectRoot).getParent().resolve("data");
    }

    @GetMapping("/upcoming")
    public ResponseEntity<List<Map<String, Object>>> getUpcomingGames() {
        try {
            File scheduleFile = dataDir.resolve("schedule/upcoming_games.json").toFile();
            
            if (scheduleFile.exists()) {
                List<Map<String, Object>> games = objectMapper.readValue(
                    scheduleFile, 
                    new TypeReference<List<Map<String, Object>>>() {}
                );
                return ResponseEntity.ok(games);
            } else {
                // Return empty list if file doesn't exist
                return ResponseEntity.ok(new ArrayList<>());
            }
        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.ok(new ArrayList<>());
        }
    }

    @GetMapping("/team-stats")
    public ResponseEntity<List<Map<String, Object>>> getTeamStats() {
        try {
            File statsFile = dataDir.resolve("processed/top10_team_stats.csv").toFile();
            
            if (statsFile.exists()) {
                List<Map<String, Object>> stats = parseCsvToList(statsFile);
                return ResponseEntity.ok(stats);
            } else {
                return ResponseEntity.ok(new ArrayList<>());
            }
        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.ok(new ArrayList<>());
        }
    }

    private List<Map<String, Object>> parseCsvToList(File csvFile) throws IOException {
        List<Map<String, Object>> result = new ArrayList<>();
        java.util.Scanner scanner = new java.util.Scanner(csvFile);
        
        if (!scanner.hasNextLine()) {
            scanner.close();
            return result;
        }
        
        // Read header
        String headerLine = scanner.nextLine();
        String[] headers = headerLine.split(",");
        
        // Read data rows
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            String[] values = line.split(",");
            
            Map<String, Object> row = new java.util.HashMap<>();
            for (int i = 0; i < headers.length && i < values.length; i++) {
                String header = headers[i].trim();
                String value = values[i].trim();
                
                // Try to parse as number
                try {
                    if (value.contains(".")) {
                        row.put(header, Double.parseDouble(value));
                    } else {
                        row.put(header, Long.parseLong(value));
                    }
                } catch (NumberFormatException e) {
                    row.put(header, value);
                }
            }
            result.add(row);
        }
        
        scanner.close();
        return result;
    }
}
