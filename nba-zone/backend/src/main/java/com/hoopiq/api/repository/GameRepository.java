package com.hoopiq.api.repository;

import com.hoopiq.api.model.Game;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface GameRepository extends JpaRepository<Game, Long> {
    
    List<Game> findByHomeTeamIdOrAwayTeamId(Long homeTeamId, Long awayTeamId);
    
    List<Game> findByStatus(Game.GameStatus status);
    
    List<Game> findBySeason(String season);
    
    @Query("SELECT g FROM Game g WHERE g.gameDate >= :startDate AND g.gameDate <= :endDate ORDER BY g.gameDate")
    List<Game> findByDateRange(LocalDateTime startDate, LocalDateTime endDate);
    
    @Query("SELECT g FROM Game g WHERE g.status = 'SCHEDULED' ORDER BY g.gameDate")
    List<Game> findUpcomingGames();
}
