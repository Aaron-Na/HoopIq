package com.hoopiq.api.controller;

import com.hoopiq.api.model.Player;
import com.hoopiq.api.service.PlayerService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/players")
public class PlayerController {

    private final PlayerService playerService;

    public PlayerController(PlayerService playerService) {
        this.playerService = playerService;
    }

    @GetMapping
    public List<Player> getAllPlayers(@RequestParam(required = false) String position,
                                       @RequestParam(required = false) String search,
                                       @RequestParam(required = false) Long teamId) {
        if (teamId != null) {
            return playerService.getPlayersByTeam(teamId);
        }
        if (position != null && !position.isEmpty()) {
            return playerService.getPlayersByPosition(position);
        }
        if (search != null && !search.isEmpty()) {
            return playerService.searchPlayers(search);
        }
        return playerService.getAllPlayers();
    }

    @GetMapping("/{id}")
    public ResponseEntity<Player> getPlayerById(@PathVariable Long id) {
        return playerService.getPlayerById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/top-scorers")
    public List<Player> getTopScorers() {
        return playerService.getTopScorers();
    }

    @PostMapping
    public Player createPlayer(@RequestBody Player player) {
        return playerService.savePlayer(player);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Player> updatePlayer(@PathVariable Long id, @RequestBody Player player) {
        return playerService.getPlayerById(id)
                .map(existingPlayer -> {
                    player.setId(id);
                    return ResponseEntity.ok(playerService.savePlayer(player));
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePlayer(@PathVariable Long id) {
        if (playerService.getPlayerById(id).isPresent()) {
            playerService.deletePlayer(id);
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
