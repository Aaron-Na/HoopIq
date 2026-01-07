package com.hoopiq.api.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "predictions")
public class Prediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "game_id", nullable = false)
    private Game game;

    @Column(nullable = false)
    private Double homeWinProbability;

    @Column(nullable = false)
    private Double awayWinProbability;

    @Column(nullable = false)
    private String predictedWinner;

    @Column(nullable = false)
    private Double confidence;

    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() { createdAt = LocalDateTime.now(); }

    public Prediction() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Game getGame() { return game; }
    public void setGame(Game game) { this.game = game; }
    public Double getHomeWinProbability() { return homeWinProbability; }
    public void setHomeWinProbability(Double homeWinProbability) { this.homeWinProbability = homeWinProbability; }
    public Double getAwayWinProbability() { return awayWinProbability; }
    public void setAwayWinProbability(Double awayWinProbability) { this.awayWinProbability = awayWinProbability; }
    public String getPredictedWinner() { return predictedWinner; }
    public void setPredictedWinner(String predictedWinner) { this.predictedWinner = predictedWinner; }
    public Double getConfidence() { return confidence; }
    public void setConfidence(Double confidence) { this.confidence = confidence; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
