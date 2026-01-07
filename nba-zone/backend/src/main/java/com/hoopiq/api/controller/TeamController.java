package com.hoopiq.api.controller;

import com.hoopiq.api.model.Team;
import com.hoopiq.api.service.TeamService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/teams")
public class TeamController {

    private final TeamService teamService;

    public TeamController(TeamService teamService) {
        this.teamService = teamService;
    }

    @GetMapping
    public List<Team> getAllTeams(@RequestParam(required = false) String conference,
                                   @RequestParam(required = false) String search) {
        if (conference != null && !conference.isEmpty()) {
            return teamService.getTeamsByConference(conference);
        }
        if (search != null && !search.isEmpty()) {
            return teamService.searchTeams(search);
        }
        return teamService.getAllTeams();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Team> getTeamById(@PathVariable Long id) {
        return teamService.getTeamById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/abbreviation/{abbr}")
    public ResponseEntity<Team> getTeamByAbbreviation(@PathVariable String abbr) {
        return teamService.getTeamByAbbreviation(abbr)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public Team createTeam(@RequestBody Team team) {
        return teamService.saveTeam(team);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Team> updateTeam(@PathVariable Long id, @RequestBody Team team) {
        return teamService.getTeamById(id)
                .map(existingTeam -> {
                    team.setId(id);
                    return ResponseEntity.ok(teamService.saveTeam(team));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTeam(@PathVariable Long id) {
        if (teamService.getTeamById(id).isPresent()) {
            teamService.deleteTeam(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
