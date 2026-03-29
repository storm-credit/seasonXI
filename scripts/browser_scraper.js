/**
 * SeasonXI Browser Scraper
 *
 * Run this in the browser console on each FBref page to collect data.
 *
 * Usage:
 * 1. Open FBref league standings page (e.g., /comps/12/2021-2022/2021-2022-La-Liga-Stats)
 *    → Run: extractTeams('laliga')
 * 2. Open FBref shooting page (e.g., /comps/12/2021-2022/shooting/2021-2022-La-Liga-Stats)
 *    → Run: extractShooting('laliga')
 * 3. Open FBref standard stats page (e.g., /comps/12/2021-2022/stats/2021-2022-La-Liga-Stats)
 *    → Run: buildAndDownload('La Liga', '2021-2022', '2021/22', 'laliga')
 *
 * League pages (comp IDs):
 * - EPL: 9
 * - La Liga: 12
 * - Serie A: 11
 * - Bundesliga: 20
 * - Ligue 1: 13
 */

function extractTeams(leagueKey) {
    const table = document.querySelector('table[id*="results"][id*="overall"]');
    const rows = table.querySelectorAll('tbody tr');
    const teams = {};
    rows.forEach(row => {
        const get = (s) => { const c = row.querySelector(`td[data-stat="${s}"], th[data-stat="${s}"]`); return c ? c.textContent.trim() : ''; };
        const team = get('team');
        if (team) teams[team] = [get('rank'), get('games'), get('goals_for'), get('goals_against'), get('points'), get('wins'), get('ties'), get('losses')].join(',');
    });
    localStorage.setItem(`seasonxi_${leagueKey}_teams`, JSON.stringify(teams));
    console.log(`✅ ${leagueKey} teams: ${Object.keys(teams).length}`);
}

function extractShooting(leagueKey) {
    const table = document.querySelector('#stats_shooting');
    const rows = table.querySelectorAll('tbody tr:not(.thead)');
    const data = {};
    rows.forEach(row => {
        if (row.classList.contains('partial_table')) return;
        const p = row.querySelector('td[data-stat="player"] a');
        if (!p) return;
        const get = (s) => { const c = row.querySelector(`td[data-stat="${s}"]`); return c ? c.textContent.trim() : '0'; };
        data[p.textContent.trim() + '|||' + get('team')] = get('shots') + ',' + get('shots_on_target');
    });
    localStorage.setItem(`seasonxi_${leagueKey}_shooting`, JSON.stringify(data));
    console.log(`✅ ${leagueKey} shooting: ${Object.keys(data).length}`);
}

function buildAndDownload(leagueName, seasonId, seasonLabel, leagueKey) {
    const shooting = JSON.parse(localStorage.getItem(`seasonxi_${leagueKey}_shooting`) || '{}');
    const teams = JSON.parse(localStorage.getItem(`seasonxi_${leagueKey}_teams`) || '{}');
    const table = document.querySelector('#stats_standard');
    const rows = table.querySelectorAll('tbody tr:not(.thead)');
    const seen = new Set();
    const header = 'player_season_id,player_id,player_name,club_id,club_name,season_id,season_label,primary_position,appearances,starts,minutes_played,goals,assists,shots,shots_on_target,key_passes,progressive_passes,progressive_carries,successful_dribbles,xg,xa,tackles,interceptions,clearances,aerial_duels_won,yellow_cards,red_cards,clean_sheets,team_goals_scored,team_goals_conceded,league_name,final_table_rank,team_points,team_wins,team_draws,team_losses';
    const lines = [header];

    rows.forEach(row => {
        if (row.classList.contains('partial_table')) return;
        const p = row.querySelector('td[data-stat="player"] a');
        if (!p) return;
        const get = (s) => { const c = row.querySelector(`td[data-stat="${s}"]`); return c ? c.textContent.trim() : '0'; };
        const name = p.textContent.trim();
        const team = get('team');
        const minutes = parseInt(get('minutes').replace(/,/g, '')) || 0;
        if (minutes < 450) return;
        const pos = get('position').toUpperCase();
        let bucket = 'FW';
        if (pos.includes('GK')) bucket = 'GK';
        else if (pos.includes('DF')) bucket = 'DF';
        else if (pos.includes('MF')) bucket = 'MF';
        const slug = name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').replace(/-+/g, '-');
        const teamSlug = team.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').replace(/-+/g, '-');
        const psid = slug + '-' + teamSlug + '-' + seasonId;
        if (seen.has(psid)) return;
        seen.add(psid);
        const shData = (shooting[name + '|||' + team] || '0,0').split(',');
        const tmData = (teams[team] || '0,0,0,0,0,0,0,0').split(',');
        const esc = (s) => s.includes(',') ? `"${s}"` : s;
        lines.push([psid, slug, esc(name), teamSlug, esc(team), seasonId, seasonLabel, bucket, get('games'), get('games_starts'), minutes, get('goals'), get('assists'), shData[0], shData[1], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, get('cards_yellow'), get('cards_red'), 0, tmData[2], tmData[3], leagueName, tmData[0], tmData[4], tmData[5], tmData[6], tmData[7]].join(','));
    });

    const csv = lines.join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${leagueKey}_${seasonId.replace('-', '_')}_players.csv`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 1000);
    console.log(`✅ ${leagueName} ${seasonId}: ${lines.length - 1} players → downloading CSV`);
}
