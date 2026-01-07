package com.hoopiq.api.service;

import com.hoopiq.api.model.Team;
import com.hoopiq.api.repository.TeamRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class TeamService {

    private final TeamRepository teamRepository;

    public TeamService(TeamRepository teamRepository) {
        this.teamRepository = teamRepository;
    }

    public List<Team> getAllTeams() {
        return teamRepository.findAll();
    }

    public Optional<Team> getTeamById(Long id) {
        return teamRepository.findById(id);
    }

    public Optional<Team> getTeamByAbbreviation(String abbreviation) {
        return teamRepository.findByAbbreviation(abbreviation);
    }

    public List<Team> getTeamsByConference(String conference) {
        return teamRepository.findByConference(conference);
    }

    public List<Team> searchTeams(String query) {
        return teamRepository.findByNameContainingIgnoreCaseOrCityContainingIgnoreCase(query, query);
    }

    public Team saveTeam(Team team) {
        return teamRepository.save(team);
    }

    public void deleteTeam(Long id) {
        teamRepository.deleteById(id);
    }
}
