# Daten einlesen
karten <- read.csv("./WAHR/data/Mythical_Island.csv", stringsAsFactors = FALSE)
karten_god_pack <- read.csv("./WAHR/data/Mythical_Island_god_pack.csv", stringsAsFactors = FALSE)

parse_percent_column <- function(x) {
  x[is.na(x) | trimws(x) == ""] <- "0%"
  as.numeric(sub("%", "", x)) / 100
}

# Normal pack probabilities
alle_karten <- karten$Name
prob_1_3 <- parse_percent_column(karten$First.third.cards)
prob_4   <- parse_percent_column(karten$Fourth.card)
prob_5   <- parse_percent_column(karten$Fifth.card)

# God pack probabilities
alle_karten_god <- karten_god_pack$Name
prob_1_3_g <- parse_percent_column(karten_god_pack$First.third.cards)
prob_4_g   <- parse_percent_column(karten_god_pack$Fourth.card)
prob_5_g   <- parse_percent_column(karten_god_pack$Fifth.card)

# MODIFIED: ziehe_pack now takes god_pack_rate
ziehe_pack <- function(current_god_pack_rate) {
  is_godpack <- runif(1) < current_god_pack_rate
  
  if (is_godpack) {
    cards_drawn <- c()
    if (length(alle_karten_god) > 0 && sum(prob_1_3_g, na.rm = TRUE) > 0) {
      cards_drawn <- c(cards_drawn, sample(alle_karten_god, size = 3, replace = TRUE, prob = prob_1_3_g))
    }
    if (length(alle_karten_god) > 0 && sum(prob_4_g, na.rm = TRUE) > 0) {
      cards_drawn <- c(cards_drawn, sample(alle_karten_god, size = 1, replace = TRUE, prob = prob_4_g))
    }
    if (length(alle_karten_god) > 0 && sum(prob_5_g, na.rm = TRUE) > 0) {
      cards_drawn <- c(cards_drawn, sample(alle_karten_god, size = 1, replace = TRUE, prob = prob_5_g))
    }
    return(cards_drawn)
  } else {
    return(c(
      sample(alle_karten, size = 3, replace = TRUE, prob = prob_1_3),
      sample(alle_karten, size = 1, replace = TRUE, prob = prob_4),
      sample(alle_karten, size = 1, replace = TRUE, prob = prob_5)
    ))
  }
}

# MODIFIED: simuliere_jahr_mit_slots now takes god_pack_rate
simuliere_jahr_mit_slots <- function(packs_pro_tag, tage = 30, current_god_pack_rate) {
  gezogen <- replicate(packs_pro_tag * tage, ziehe_pack(current_god_pack_rate), simplify = FALSE)
  gezogen <- unlist(gezogen)
  if (length(gezogen) == 0) return(0)
  length(unique(gezogen))
}

# --- Simulation Setup ---
N <- 1000 
tage_vektor <- c(7, 14, 30) 
god_pack_chance_vektor <- c(0.0005, 0.01, 0.05) 
kosten_premium_pro_monat <- 10 

ergebnisse_gesamt <- list() 

# --- Main Simulation Loop ---
for (gp_chance in god_pack_chance_vektor) {
  ergebnisse_fuer_gp_chance <- list()
  cat(paste("\nSimulating for God Pack Chance:", gp_chance * 100, "%\n"))
  
  for (tage in tage_vektor) {
    cat(paste("  Simulating for", tage, "days...\n"))
    gratis <- as.numeric(replicate(N, simuliere_jahr_mit_slots(2, tage = tage, current_god_pack_rate = gp_chance)))
    premium <- as.numeric(replicate(N, simuliere_jahr_mit_slots(4, tage = tage, current_god_pack_rate = gp_chance)))
    
    mean_diff <- mean(premium - gratis, na.rm = TRUE)
    if (is.na(mean_diff) || is.nan(mean_diff)) mean_diff <- 0
    
    kosten <- (tage / 30) * kosten_premium_pro_monat
    kosten_pro_extra <- if (mean_diff > 0) kosten / mean_diff else NA
    
    ergebnisse_fuer_gp_chance[[as.character(tage)]] <- list(
      tage = tage,
      gratis = gratis,
      premium = premium,
      kosten = kosten,
      extra_karten = mean_diff,
      kosten_pro_extra = kosten_pro_extra
    )
  }
  ergebnisse_gesamt[[as.character(gp_chance)]] <- ergebnisse_fuer_gp_chance
}

# --- Prepare Data for Multivariate Faceted Plotting ---
library(ggplot2)
all_plot_data_list_multivariate <- list()

for (gp_chance_char in names(ergebnisse_gesamt)) {
  ergebnisse_fuer_gp_chance <- ergebnisse_gesamt[[gp_chance_char]]
  current_gp_rate <- as.numeric(gp_chance_char) 

  for (tage_val in tage_vektor) {
    tage_char <- as.character(tage_val)
    
    temp_df <- data.frame(
      Karten = c(ergebnisse_fuer_gp_chance[[tage_char]]$gratis,
                 ergebnisse_fuer_gp_chance[[tage_char]]$premium),
      Modell = rep(c("Gratis", "Premium"), each = N),
      Tage = factor(tage_val),
      GodPackRate = factor(paste0(current_gp_rate * 100, "%")) 
    )
    list_key <- paste("gp", current_gp_rate, "tage", tage_val, sep = "_")
    all_plot_data_list_multivariate[[list_key]] <- temp_df
  }
}

# --- Create and Print the Multivariate Faceted Plot ---
combined_df_multivariate <- do.call(rbind, all_plot_data_list_multivariate)
rownames(combined_df_multivariate) <- NULL 

p_multi_faceted <- ggplot(combined_df_multivariate, aes(x = Karten, fill = Modell)) +
  geom_bar(position = "dodge", color = "black") +
  facet_grid(GodPackRate ~ Tage, scales = "free_y", labeller = label_both) + 
  labs(
    title = "Verteilung der Kartenzahl nach Tagen und God Pack Häufigkeit",
    x = "Anzahl verschiedener Karten",
    y = "Anzahl Simulationen",
    fill = "Modell"
  ) +
  theme_minimal() +
  theme(legend.position = "top",
        strip.text.x = element_text(size = 9), 
        strip.text.y = element_text(size = 9),
        plot.title = element_text(hjust = 0.5)) 

print(p_multi_faceted)

cat("\nMultivariate simulation and plotting complete.\n")