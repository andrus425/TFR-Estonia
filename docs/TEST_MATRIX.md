# Manual campaign and release matrix

Use the pinned TFR baseline and a clean two-mod playset. Start fresh campaigns;
record the game version, DLC selection, scenario, save and new errors relative
to the parent-only baseline. Completion is not implied by the presence of scripts.

| Scenario | Required observation |
|---|---|
| Player EST / AI Russia | Ratas leader, 57-seat coalition, 101 total seats, working tree, no no-content warning, EU/NATO/economy retained |
| AI EST / observer country | Research, production, recruiting, focuses and decisions remain active |
| Player Russia / AI EST | Stronger parent NATO penalty works initially; preparation lifts it once for EST |
| Seven party routes | Each reaches government through valid confidence; ten policy focuses and both-war choices are accessible |
| Same-ideology coalition | Reform/PP and Centre/E200 remain separate; opposition seats grant no coalition bonus |
| Elections | 5% threshold, deterministic ties, 101 seats, invalid input recovery, caretaker and snap elections |
| Party emergence | E200 exists outside parliament initially; PP appears from Aug 2022; polling remains normalized |
| Cohesion/readiness | UI values/trends match modifiers; thresholds and cancellations are correct |
| Procurement/reserves | Budget charged, cooldown respected, no duplicate authorization or free reserve army |
| First war / NATO victory | Entry, Tallinn capture hooks, political responses and reconstruction progress |
| Communist Russia victory | Same EST tag survives, patron and communist mandate correct, Russian follow-up content progresses |
| Medvedev/Mironov victory | EST keeps 13/191; 840/1329 transferred; civilian occupation is playable |
| Nationalist/military victory | Former full annex becomes Northern Estonia occupation; parent remaining transfers still occur |
| Eurasian victory | Dugin occupation and later second-war scripts preserve the same country |
| Liberal/Baltic federation | Regional administration gets intended remainder; EST remains alongside it |
| European supervised victory | Correct patron, supervised mandate, valid sovereignty negotiation |
| German/TTS authoritarian victory | TTS receives intended remaining states; EST keeps Northern Estonia under direct patron |
| Russian pacification | Only Soviet-owned territories evaluated; keeping EST alive does not skip requirements |
| Second defeat/new patron | New mandate selects once; no duplicated investments, factories, armies or rewards |
| Restoration | Correct provisional PM/presidency, main-tree history preserved, election within 90 days |
| Save/reload | Before/after election, pending settlement, occupation installation, restoration and timed decision |
| DLC branches | With/without Man the Guns and By Blood Alone, inherited army/navy/air setup remains valid |
| Rendered interface | Parliament at common resolutions/UI scales; focus grid, event text, icons and tooltips inspected |
| Full campaigns | Ordinary campaign for each party; representative hands-off runs through both wars |

Useful documented console helpers include `event <event_id> EST`, `freefocuses`,
`focus_count EST`, `tdebug`, `loc_check`, `loc_check_focuses`, `loc_check_events`,
`loc_check_decisions`, `loc_check_characters`, and `loc_check_national_spirits`.
Return to normal play for campaign acceptance; accelerated commands do not prove
balance, natural event scheduling or legitimate route accessibility.
