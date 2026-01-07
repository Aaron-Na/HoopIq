package com.hoopiq.api.repository;

import com.hoopiq.api.model.Prediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PredictionRepository extends JpaRepository<Prediction, Long> {
    
    Optional<Prediction> findByGameId(Long gameId);
}
