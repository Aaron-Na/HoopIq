package com.hoopiq.api.repository;

import com.hoopiq.api.model.Player;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PlayerRepository extends JpaRepository<Player, Long> {
    
    List<Player> findByTeamId(Long teamId);
    
    List<Player> findByPosition(String position);
    
    List<Player> findByIsActiveTrue();
    
    @Query("SELECT p FROM Player p WHERE LOWER(p.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(p.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<Player> searchByName(String name);
    
    @Query("SELECT p FROM Player p ORDER BY p.ppg DESC")
    List<Player> findTopScorers();
}
