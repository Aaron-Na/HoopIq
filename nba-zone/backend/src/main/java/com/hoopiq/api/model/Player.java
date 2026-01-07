package com.hoopiq.api.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import jakarta.persistence.*;

@Entity
@Table(name = "players")
public class Player {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "team_id")
    @JsonIgnoreProperties({"hibernateLazyInitializer", "handler"})
    private Team team;

    private String position;
    private Integer jerseyNumber;
    private String height;
    private String weight;
    private String college;
    private String country;
    private Double ppg;
    private Double rpg;
    private Double apg;
    private String imageUrl;
    private Boolean isActive;

    public Player() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    public Team getTeam() { return team; }
    public void setTeam(Team team) { this.team = team; }
    public String getPosition() { return position; }
    public void setPosition(String position) { this.position = position; }
    public Integer getJerseyNumber() { return jerseyNumber; }
    public void setJerseyNumber(Integer jerseyNumber) { this.jerseyNumber = jerseyNumber; }
    public String getHeight() { return height; }
    public void setHeight(String height) { this.height = height; }
    public String getWeight() { return weight; }
    public void setWeight(String weight) { this.weight = weight; }
    public String getCollege() { return college; }
    public void setCollege(String college) { this.college = college; }
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }
    public Double getPpg() { return ppg; }
    public void setPpg(Double ppg) { this.ppg = ppg; }
    public Double getRpg() { return rpg; }
    public void setRpg(Double rpg) { this.rpg = rpg; }
    public Double getApg() { return apg; }
    public void setApg(Double apg) { this.apg = apg; }
    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }
    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }
}
