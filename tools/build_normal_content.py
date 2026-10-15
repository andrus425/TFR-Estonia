from pathlib import Path
import argparse, json, re
from native_script_interface import amount_call, native_amount_calls
from build_opening_content import POLICIES
from build_ratas_continuation import POLICIES as RATAS_POLICIES
from build_kallas_continuation import POLICIES as KALLAS_POLICIES

parser = argparse.ArgumentParser(description='Build Estonia normal content.')
parser.add_argument('--focus-only', action='store_true', help='Update the tree, route AI, focus text and dependent decisions without rewriting events or reward ideas.')
args = parser.parse_args()

ROOT = Path(__file__).resolve().parents[1]
P = 'TFR_EST_'
loc = {}
focuses = []
parties = [('reform',1,'Reform'),('centre',2,'Keskerakond'),('ekre',3,'EKRE'),('isamaa',4,'Isamaa'),('sde',5,'Social Democrats'),('e200',6,'Eesti 200'),('pp',7,'Parempoolsed')]

def L(key, text):
    loc[key] = text
    return key

def co(n): return amount_call('TFR_EST_change_cohesion', n)
def rd(n): return amount_call('TFR_EST_change_readiness', n)
def budget(n): return amount_call('TFR_EST_spend_budget', n)
def pp(n): return f'add_political_power = {n}'
def xp(n): return f'army_experience = {n}'
def idea(s): return f'add_ideas = TFR_EST_{s}'
def flag(s): return f'set_country_flag = TFR_EST_{s}'
def event(n): return f'country_event = {{ id = tfr_estonia_content.{n} }}'
def reward(*parts): return '\n'.join(parts)
def build(state, typ, levels=1):
    shared = '\nadd_extra_state_shared_building_slots = 1' if typ in ('industrial_complex','arms_factory','dockyard') else ''
    return f'{state} = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT }}{shared}\nadd_building_construction = {{ type = {typ} level = {levels} instant_build = yes }} }} }}'

def fort(state, province):
    return f'{state} = {{ if = {{ limit = {{ is_owned_by = ROOT is_controlled_by = ROOT ROOT = {{ controls_province = {province} }} }} add_building_construction = {{ type = bunker province = {province} level = 1 instant_build = yes }} }} }}'

def F(suffix, name, desc, x, y, pre=None, effects='', icon='national_unity', cost=5, avail='', party=None, priority=5):
    ident = P + suffix
    L(ident,name); L(ident+'_desc',desc)
    tests = ['NOT = { has_country_flag = TFR_EST_occupied }']
    branch_tests = ['has_country_flag = TFR_EST_opening_complete']
    crisis = any(token in avail for token in ('TFR_EST_campaign_stage', 'TFR_EST_restoration_pending', 'TFR_EST_first_war_seen', 'TFR_EST_second_war_seen'))
    if not crisis:
        tests += ['TFR_EST_coalition_majority = yes', 'NOT = { has_country_flag = TFR_EST_caretaker }', 'TFR_EST_show_legacy_domestic_tree = yes']
        branch_tests.append('TFR_EST_show_legacy_domestic_tree = yes')
    if party is not None:
        tests += [f'check_variable = {{ TFR_EST_pm_party = {party} }}','NOT = { has_country_flag = TFR_EST_caretaker }']
        branch_tests += [f'check_variable = {{ TFR_EST_pm_party = {party} }}', 'NOT = { has_country_flag = TFR_EST_caretaker }']
    if crisis or 'TFR_EST_active_pp' in avail:
        branch_tests.append(avail)
    if avail: tests.append(avail)
    pr = [] if pre is None else ([pre] if isinstance(pre,str) else pre)
    if pr == ['opening_marriage_referendum']:
        # A failed opening is hidden and occupation may remove native focus
        # records. Use its persistent resolved stage for these new phase roots;
        # every internal branch keeps its normal native prerequisites.
        pr = []
        tests.append('TFR_EST_opening_resolved = yes')
    prereqs = ''.join(f'        prerequisite = {{ focus = TFR_EST_{s} }}\n' for s in pr)
    f = f'''\n\tfocus = {{
        id = {ident}
        icon = GFX_goal_generic_{icon}
        x = {x}
        y = {y + 7}
        cost = {cost}
{prereqs}        allow_branch = {{ {' '.join(branch_tests)} }}
        available = {{ {' '.join(tests)} }}
        bypass = {{ has_country_flag = TFR_EST_done_{suffix} }}
        cancel_if_invalid = yes
        continue_if_invalid = no
        ai_will_do = {{ factor = {priority} }}
        completion_reward = {{
            set_country_flag = TFR_EST_done_{suffix}
            {effects}
        }}
    }}\n'''
    focuses.append((ident,f,party))

# The mandatory opening is defined in build_opening_content.py.

# Every programme remains in the same tree. A later elected cabinet can enact its own reforms.
programmes = {
'centre':[
('cabinet','A Coalition That Delivers','Jüri Ratas’s government must make coalition management serve practical administration. Establish an agreed legislative calendar and protect cabinet decisions from competing ministerial campaigns.',reward(co(3),pp(50)),'national_unity'),
('municipal_compact','The Municipal Compact','Keskerakond’s strength rests on local institutions. Negotiate a predictable funding agreement with towns and rural municipalities, with transparent service targets rather than favors for party allies.',reward(budget(50),co(4)),'consumer_goods'),
('regional_transport','Connect the Counties','Residents outside Tallinn need access to jobs, hospitals and schools. Improve transport links in Estonian Livonia through a funded regional programme.',reward(budget(100),build(191,'infrastructure')),'construct_infrastructure'),
('family_security','Security for Working Families','Protect household incomes through better coordination of benefits and employment services. The programme will reduce insecurity, though coalition partners will demand that its expenditure remains visible.',reward(budget(55),co(4),pp(-20)),'consumer_goods'),
('integration','A Common Civic Home','A shared Estonian civic identity should include loyal residents of every background. Fund language learning and local participation, giving Ida-Viru’s communities a practical stake in the republic’s future.',reward(budget(35),co(5),event(10)),'national_unity'),
('fair_procurement','Clean Up Public Procurement','Local development loses legitimacy when contracts seem designed for insiders. Introduce external audits and publish tender decisions even where they embarrass influential supporters.',reward(co(4),pp(-25)),'political_pressure'),
('urban_industry','Urban Employment Partnerships','Municipalities and manufacturers can prepare serviced industrial sites around Tallinn. Commit public funds to infrastructure while leaving hiring and production to firms.',reward(budget(200),build(13,'industrial_complex')),'construct_civ_factory'),
('broad_defence','A Broad Defence Coalition','National defence requires public consent beyond any single party. Bring mayors, employers and reservists into preparedness planning and compensate essential workers for reserve exercises.',reward(budget(40),rd(5),co(2)),'defence'),
('social_war_compact','The Social War Compact','If war comes, compensation for displaced families and clear rules for requisitioning will be as important as mobilization orders. Write those guarantees before emergency pressure makes them impossible to debate.',reward(budget(40),co(4),rd(2)),'major_war'),
('programme','Government for the Whole Republic','Complete a governing settlement that combines local investment, accountable social protection and a broad commitment to defence. Its administrative benefits remain active while a Keskerakond prime minister holds office.',reward(flag('centre_programme'),'TFR_EST_refresh_programme = yes',event(17)),'national_unity')],
'reform':[
('cabinet','A Reform Government','Kaja Kallas’s Reform Party offers a government centered on administrative competence, European cooperation and enterprise. A cabinet must turn that promise into laws capable of winning parliamentary support.',reward(co(2),pp(60)),'political_pressure'),
('digital_services','One Door to Public Services','Citizens should not submit the same information to several offices. Link public services through secure records while maintaining access for people who cannot use the digital system.',reward(budget(35),co(3)),'scientific_exchange'),
('investment','A Predictable Investment Climate','Clear licensing and predictable contracts attract productive investment. Remove unnecessary delays while protecting the standards that make Estonia a reliable place to do business.',reward(budget(50),pp(40)),'trade'),
('budget_review','Review Every Commitment','Expenditure already promised can consume the freedom of any future cabinet. Review subsidies and overlapping agencies, then let parliament decide which savings justify their social cost.',reward(pp(35),event(11)),'consumer_goods'),
('tartu_innovation','Tartu Innovation Partnerships','Universities, engineers and businesses in Tartu can develop products for a changing world. Fund practical research partnerships and retain the skilled workforce that makes them possible.',reward(budget(180),build(1329,'industrial_complex')),'scientific_exchange'),
('school_access','Digital Access Beyond Tallinn','A digital state must work for rural schools and low-income families. Expand access, training and support so modernization does not deepen regional inequality.',reward(budget(45),co(4)),'consumer_goods'),
('european_networks','Keep European Networks Open','Trade, research and diplomatic cooperation are more valuable when Europe is unstable. Keep officials engaged with functioning European institutions and preserve practical links despite political disagreements.',reward(pp(45),co(2)),'alliance'),
('precision_defence','Precision and Professionalism','A small armed force cannot afford wasted training or incompatible procurement. Emphasize skilled personnel, interoperable communications and equipment that Estonia can maintain.',reward(budget(60),rd(5),xp(15)),'defence'),
('crisis_transparency','Transparent Emergency Government','Emergency measures should have clear purposes, reporting duties and expiry dates. Preserve trust through published objectives even when the cabinet must act quickly.',reward(co(4),rd(2)),'national_unity'),
('programme','An Open and Capable Republic','Conclude the Reform programme with secure public services, productive investment and disciplined administration. Its active cabinet benefits require a Reform prime minister; enacted laws survive subsequent elections.',reward(flag('reform_programme'),'TFR_EST_refresh_programme = yes',event(17)),'trade')],
'ekre':[
('cabinet','A National Conservative Cabinet','Mart Helme’s EKRE seeks a stronger voice for national sovereignty and conservative voters. Effective government will require the movement to accept the obligations of a parliamentary cabinet.',reward(pp(60),co(1)),'national_unity'),
('local_voice','Hear the Counties','Rural communities should have a voice in decisions that reshape their economy and services. Organize county consultations with published commitments and a budget for local priorities.',reward(budget(40),co(4)),'consumer_goods'),
('sovereignty_review','Review External Commitments','Examine international commitments and explain their practical costs and protections to parliament. Choose whether confrontation or negotiation better serves sovereignty in a dangerous world.',reward(pp(35),event(12)),'political_pressure'),
('border_service','Strengthen the Border Service','Improve communications, observation and contingency planning along the eastern border. Border officers need working systems and clear procedures, rather than political declarations alone.',reward(budget(55),rd(4),build(840,'anti_air_building')),'defence'),
('rural_enterprise','Rural Enterprise Grants','Small producers and local firms can sustain communities that lose workers to Tallinn. Support viable workshops and servicing capacity in Estonian Livonia.',reward(budget(160),build(191,'industrial_complex')),'construct_civ_factory'),
('family_policy','A Family Policy for the Future','Conservative family policy must address housing, work and access to local services. Fund practical assistance while keeping access to essential services clear for all citizens.',reward(budget(50),co(3)),'consumer_goods'),
('civil_duty','Civil Duty in Every County','A culture of preparedness can bring citizens into first aid, emergency logistics and local defence. Coordinate voluntary service with municipalities and Kaitseliit instructors.',reward(budget(35),rd(5),co(2)),'army_doctrines'),
('domestic_workshops','Equipment from Domestic Workshops','Maintenance, protective equipment and simple military supplies offer a realistic role for Estonian industry. Fund contracts with local manufacturers rather than promising a self-sufficient heavy arms sector.',reward(budget(220),build(191,'arms_factory')),'construct_mil_factory'),
('wartime_sovereignty','Sovereignty Through Survival','War will force cooperation with states whose politics differ from ours. A national defence doctrine should preserve Estonian command while making allied support practical.',reward(rd(4),xp(15),co(2)),'major_war'),
('programme','A Republic Ready to Stand','Complete the national conservative programme with local organization, family support and practical defence. Its cabinet bonuses remain active while EKRE leads a confirmed government.',reward(flag('ekre_programme'),'TFR_EST_refresh_programme = yes',event(17)),'national_unity')],
'isamaa':[
('cabinet','A Government of National Institutions','Helir-Valdor Seeder’s Isamaa places national continuity at the center of government. A smaller parliamentary party must find partners for policies that should outlast the cabinet that adopts them.',reward(pp(55),co(2)),'national_unity'),
('language','Estonian Language and Opportunity','Language education should create opportunity and a shared civic space. Train teachers and support adult learners, connecting national identity with practical participation.',reward(budget(35),co(4)),'consumer_goods'),
('family_housing','Homes for Young Families','Reliable housing and local services can help families build a future in Estonia. A measured guarantee programme will support viable homes without replacing private lending.',reward(budget(60),co(3)),'construct_civ_factory'),
('energy_security','Energy Security as National Policy','Estonia must reduce exposure to unreliable suppliers while keeping power affordable. Resolve the tradeoff between transition investment, local employment and immediate resilience.',reward(budget(55),event(13)),'oil_refinery'),
('county_institutions','Keep County Institutions Working','Local schools, service offices and emergency authorities sustain national institutions far from Tallinn. Combine overlapping administration while preserving a dependable presence.',reward(budget(35),co(4)),'national_unity'),
('national_industry','Industry for National Resilience','A small but reliable manufacturing base can supply tools, spares and essential products. Prepare a new civilian production site in Tartu.',reward(budget(180),build(1329,'industrial_complex')),'construct_civ_factory'),
('territorial_defence','Territorial Defence Doctrine','Kaitseliit, reservists and the regular army need common plans for protecting critical places. Exercise clear command responsibilities and routes for supporting the field army.',reward(budget(45),rd(5),xp(15)),'defence'),
('strategic_routes','Protect Strategic Routes','Roads through Tartu connect local forces with national reserves and allied supply. Improve capacity and prepare alternative movement plans before a crisis.',reward(budget(80),build(1329,'infrastructure'),rd(2)),'construct_infrastructure'),
('constitutional_continuity','Constitutional Continuity in War','Publish the legal chain of authority for a government under attack. Neither a destroyed office nor an absent minister should leave the republic without a lawful decision.',reward(co(4),rd(3)),'political_pressure'),
('programme','The Republic Across Generations','Bring family security, national institutions and territorial defence into a durable governing programme. Its cabinet benefits require an Isamaa prime minister, while completed legislation persists.',reward(flag('isamaa_programme'),'TFR_EST_refresh_programme = yes',event(17)),'national_unity')],
'sde':[
('cabinet','A Social Democratic Government','Indrek Saar’s Social Democrats seek a cabinet that makes security tangible in daily life. Public services and fair work must be funded alongside the defence of the republic.',reward(co(3),pp(50)),'consumer_goods'),
('labour_compact','The Labour Compact','Employers, workers and government can agree predictable rules for wages, retraining and emergency work. A negotiated settlement will reduce disruption when the economy comes under pressure.',reward(budget(35),co(4)),'national_unity'),
('health_network','A Reliable Health Network','Regional healthcare cannot depend on a few exhausted staff or distant facilities. Invest in coordinated services and contingency staffing across Estonia.',reward(budget(80),co(4)),'consumer_goods'),
('social_budget','Finance the Social Contract','The government must choose how to fund expanded services without losing the means to defend them. Put the tradeoff before parliament and explain the distribution of its costs.',reward(pp(25),event(14)),'political_pressure'),
('training_jobs','Retraining for Productive Jobs','Workers facing industrial change need skills that lead to actual employment. Combine retraining with practical employer partnerships and local workshop development.',reward(budget(160),build(191,'industrial_complex')),'construct_civ_factory'),
('inclusive_republic','An Inclusive Civic Republic','Inclusion strengthens security when it offers clear rights, responsibilities and access to public life. Support civic organizations and language education across divided communities.',reward(budget(30),co(5)),'national_unity'),
('civil_resilience','Resilience Begins at Home','Public shelters, trained volunteers and continuity of essential services reduce the impact of war on civilians. Integrate municipal plans with the national emergency system.',reward(budget(50),rd(4),co(2)),'defence'),
('service_families','Protect Service Families','Reservists will serve more effectively when their families retain income, childcare and access to essential services. Fund those guarantees and make them easy to claim.',reward(budget(45),rd(4),co(3)),'army_doctrines'),
('fair_requisition','Fair Rules for Emergency Work','Military logistics may require civilian equipment and labor. Set compensation and appeal procedures before those demands undermine trust in the government.',reward(co(4),xp(10)),'major_war'),
('programme','Security Through Solidarity','Complete a social democratic programme of accessible services, fair work and civil preparedness. Its active cabinet benefits depend on a Social Democratic prime minister.',reward(flag('sde_programme'),'TFR_EST_refresh_programme = yes',event(17)),'consumer_goods')],
'e200':[
('cabinet','A New Mandate for Eesti 200','Kristina Kallas’s Eesti 200 must prove that long-term plans can survive the practical demands of parliament. A new cabinet will need clear goals and partners willing to judge results.',reward(pp(55),co(2)),'political_pressure'),
('long_plan','A Plan Beyond One Election','Publish a rolling programme for education, productivity and state capacity. Give each ministry measurable milestones that parliament can revisit after the next election.',reward(co(3),pp(35)),'scientific_exchange'),
('teachers','Invest in Teachers','Education reform begins with trained and supported teachers. Fund professional development and strengthen schools that struggle to retain staff.',reward(budget(70),co(4)),'consumer_goods'),
('institutional_redesign','Redesign the State Carefully','Reducing administrative duplication can improve services, but abrupt mergers can destroy local knowledge. Decide how quickly reform should proceed and where local access needs protection.',reward(pp(25),event(15)),'political_pressure'),
('university_industry','Bridge Universities and Industry','Tartu’s researchers and employers can translate skills into products and services. Fund shared facilities and a civilian industrial site with accountable milestones.',reward(budget(180),build(1329,'industrial_complex')),'scientific_exchange'),
('shared_schools','Schools for a Shared Future','Education should equip every pupil to participate in Estonian public life. Invest in language support and common opportunities while helping teachers manage the transition.',reward(budget(50),co(5)),'national_unity'),
('future_services','Design Services Around People','Citizens experience government through the services they need, not the ministry that owns them. Reorganize access and information around life events and local needs.',reward(budget(30),co(4)),'consumer_goods'),
('adaptive_defence','Adaptive Defence Planning','A long-term defence plan must still adapt to battlefield evidence. Link training, procurement and civilian expertise through an annual review of realistic capabilities.',reward(budget(45),rd(5),xp(15)),'defence'),
('future_after_war','Plan for the Future During Crisis','Even in war, Estonia needs a plan for schools, industry and institutions afterward. Establish a reconstruction planning team that can work alongside the emergency cabinet.',reward(co(3),rd(3),pp(30)),'construct_infrastructure'),
('programme','A State Built for the Future','Complete Eesti 200’s programme of education, institutional reform and measured long-term planning. Its active cabinet benefits require an Eesti 200 prime minister.',reward(flag('e200_programme'),'TFR_EST_refresh_programme = yes',event(17)),'scientific_exchange')],
'pp':[
('cabinet','A Parempoolsed Government','Lavly Perling’s Parempoolsed offers administrative efficiency, enterprise and fiscal discipline. Its first government must establish authority through a valid coalition and a concrete legislative programme.',reward(pp(60),co(1)),'political_pressure'),
('audit','Audit the Administration','Map overlapping duties and subsidies before promising savings. Publish the evidence so reductions are judged by services preserved and resources freed, rather than the number of offices closed.',reward(pp(35),co(2)),'consumer_goods'),
('enterprise_rules','Clear Rules for Enterprise','Simpler procedures can help firms invest, hire and compete. Remove duplication while preserving predictable enforcement of the standards that protect confidence in the market.',reward(budget(35),pp(40)),'trade'),
('fiscal_choice','The Fiscal Discipline Debate','Spending restraint has costs for communities that depend on public services. Choose how quickly consolidation should proceed and explain how vulnerable households will be protected.',reward(pp(30),event(16)),'political_pressure'),
('industrial_sites','Service Productive Investment','Government can provide reliable infrastructure without trying to choose every successful business. Develop a serviced civilian manufacturing site in Northern Estonia.',reward(budget(170),build(13,'industrial_complex')),'construct_civ_factory'),
('justice_capacity','Competent and Independent Justice','Contracts and public confidence depend on effective courts and accountable prosecution. Improve administration without compromising the independence of legal decisions.',reward(budget(25),co(4)),'national_unity'),
('targeted_services','Target Help Where It Works','Review benefits and service contracts against their outcomes. Redirect limited funds toward demonstrable need while keeping application procedures accessible.',reward(budget(25),co(3)),'consumer_goods'),
('procurement_discipline','Defence Procurement Discipline','Military readiness requires equipment that can be afforded throughout its service life. Audit maintenance, training and interoperability costs before signing major contracts.',reward(budget(35),rd(4),xp(15)),'military_deal'),
('crisis_reserves','Maintain a Crisis Reserve','Fiscal planning should leave room for emergency response. Establish a documented reserve programme and clear procedures for parliamentary scrutiny when it is used.',reward(budget(40),rd(3),co(2)),'defence'),
('programme','A Lean and Reliable State','Complete a programme of productive enterprise, disciplined public contracts and competent essential services. Its active benefits depend on a Parempoolsed prime minister.',reward(flag('pp_programme'),'TFR_EST_refresh_programme = yes',event(17)),'trade')]
}
for idx,(suffix,party_id,label) in enumerate(parties):
    previous = 'opening_marriage_referendum'
    for row,(node,name,desc,eff,icon) in enumerate(programmes[suffix]):
        current = suffix+'_'+node
        F(current,name,desc,idx*3,row+6,previous,eff,icon,party=party_id,avail='check_variable = { TFR_EST_active_pp = 1 }' if suffix=='pp' else '',priority=8)
        previous = current

# Shared economic development. Three distinct chains prevent a new cabinet resetting investment.
economic = [
('digital',[('secure_records','Secure Public Records','Protect digital services with offline backups, access audits and rehearsed recovery procedures. Secure records are a foundation of ordinary administration and wartime continuity.',reward(budget(35),idea('secure_digital_state')),'intelligence_exchange'),
('technical_training','Technical Skills for Estonia','Expand practical training in electronics, maintenance and software support. A technically capable workforce is useful to employers, public services and the armed forces.',reward(budget(45),co(2)),'scientific_exchange'),
('tartu_research','Tartu Research Cooperation','Connect universities with practical research projects that Estonia can afford. Funding must concentrate on maintainable capabilities rather than prestige facilities.',reward(budget(50),idea('research_partnerships')),'scientific_exchange'),
('rural_broadband','Connect Rural Public Services','Improve the reliability of public communications outside the capital. Local offices require connectivity and trained staff to provide services during an emergency.',reward(budget(50),co(3),rd(1)),'radar'),
('cyber_exercises','National Cyber Exercises','Test how public services respond when networks are interrupted or records are compromised. The value lies in discovering weaknesses before an attacker does.',reward(budget(25),rd(3),pp(25)),'intelligence_exchange'),
('digital_civic_compact','A Digital Civic Compact','Explain how the state uses data and how citizens can challenge errors. Strong safeguards make secure systems useful and preserve trust when emergency powers expand.',reward(co(4),event(20)),'national_unity')]),
('industry',[('industrial_survey','Survey the Industrial Base','Identify workshops, manufacturers and maintenance firms capable of supporting national resilience. Production plans must begin with facilities and skills that actually exist.',reward(pp(40),flag('industrial_survey')),'production'),
('tallinn_industry','Tallinn Industrial Development','Provide a serviced production site in Northern Estonia and support viable manufacturers. This investment expands civilian capacity while adding a visible public debt commitment.',reward(budget(220),build(13,'industrial_complex')),'construct_civ_factory'),
('livonia_logistics','Livonian Logistics Improvements','Improve the routes linking southern communities, industrial sites and national distribution networks. Civil transport and military supply share the same bridges and roads.',reward(budget(100),build(191,'infrastructure'),rd(1)),'construct_infrastructure'),
('defence_contracts','Practical Defence Contracts','Domestic firms can produce basic supplies, repair equipment and improve maintenance. Fund a modest defence production facility in Estonian Livonia.',reward(budget(260),build(191,'arms_factory')),'construct_mil_factory'),
('maintenance_network','A National Maintenance Network','Build common arrangements for tools, spares and repair skills. A reliable maintenance network extracts more value from limited industrial capacity.',reward(budget(45),idea('maintenance_network'),rd(2)),'production2'),
('productive_republic','A Productive Small Republic','Coordinate vocational training, infrastructure and investment decisions around a realistic industrial strategy. Estonia should produce what it can maintain and cooperate for the rest.',reward(pp(50),co(3)),'trade')]),
('energy',[('energy_audit','Audit Energy Security','Catalogue supply dependencies, grid bottlenecks and emergency demand. A clear picture of the system is required before deciding which expensive investments matter most.',reward(pp(35),rd(2)),'oil_refinery'),
('ida_viru_transition','Ida-Viru Employment and Energy','Changes to the energy system threaten livelihoods in Ida-Viru. Fund training and civilian industrial capacity so resilience does not leave the region without a future.',reward(budget(240),build(840,'industrial_complex'),co(3)),'construct_civ_factory'),
('grid_resilience','A More Resilient Grid','Improve redundancy and emergency repair arrangements in the north-east. Power systems need workable alternative routes, stocked spares and trained repair teams.',reward(budget(100),build(840,'infrastructure'),rd(2)),'construct_infrastructure'),
('emergency_energy','Emergency Energy Stocks','Allocate funds to emergency fuel distribution and essential-service supply plans. Stock management and transport agreements matter more than a paper promise of self-sufficiency.',reward(budget(65),rd(4)),'oil_refinery'),
('affordable_heat','Reliable Heat for Households','Municipal heating and emergency shelter plans should keep homes habitable under pressure. Target assistance at vulnerable residents and protect essential repairs.',reward(budget(50),co(4)),'consumer_goods'),
('resilient_utilities','Utilities That Can Survive a Crisis','Complete joint exercises between municipalities, utilities and emergency authorities. The resulting plans will improve preparedness without replacing future maintenance expenditure.',reward(budget(25),rd(3),co(2)),'defence')])]
for col,(name,nodes) in enumerate(economic):
    previous='opening_marriage_referendum'
    for row,(s,title,desc,eff,icon) in enumerate(nodes):
        F(s,title,desc,23+col*3,row+2,previous,eff,icon,priority=8 if row<2 else 5)
        previous=s

military = [
('reserves',[('reserve_register','Audit the Reserve Register','Confirm reservist records, employers and assigned specialties. Readiness depends on knowing whom the army can call and how those people reach their units.',reward(budget(20),rd(4)),'army_doctrines'),
('kaitseliit_training','Kaitseliit Training Standards','The Defence League gives Estonia reach beyond the regular force. Improve instructor standards and common procedures so local initiative supports coherent national plans.',reward(budget(35),rd(4),xp(15),idea('kaitseliit_network')),'special_forces'),
('reserve_training_exercise','Exercise the Reserves','Fund an integrated reserve exercise with transport, communications and employer coordination. Training will reveal shortages that must be met through normal procurement.',reward(budget(50),rd(6),xp(20)),'army_doctrines'),
('reserve_depots','Dispersed Reserve Depots','Organize secure stores and issue procedures away from a few obvious facilities. Maintainability and inventory control will determine whether those stocks reach the right units.',reward(budget(45),rd(4)),'small_arms'),
('mobilization_plans','A Mobilization Plan That Works','Approve recruitment and training plans for additional reserve units. The decision remains available when readiness is sufficient; soldiers and equipment must still enter through the normal recruitment system.',reward(rd(3),flag('reserve_plan'),'custom_effect_tooltip = TFR_EST_reserve_plan_tt'),'army_doctrines'),
('total_defence','Total Defence, Clear Responsibilities','Integrate the regular army, reserve recruitment, Kaitseliit and municipal services without confusing their roles. Total defence is a disciplined plan for a small state to survive.',reward(budget(35),rd(4),idea('total_defence')),'defence')]),
('logistics',[('logistics_audit','Audit Wartime Logistics','Survey roads, fuel distribution, repair capacity and likely congestion. Plans should begin with the actual movement of forces and supplies, including support from allies.',reward(budget(20),rd(3),xp(10)),'army_motorized'),
('northern_routes','Improve Northern Supply Routes','Expand movement capacity around the capital and its approaches. Reliable roads help civilian evacuation and the timely distribution of military supplies.',reward(budget(110),build(13,'infrastructure'),rd(2)),'construct_infrastructure'),
('tartu_distribution','The Tartu Distribution Network','Strengthen the southern distribution network with improved infrastructure and rehearsed convoy routing. Supplies must move even when a major road is interrupted.',reward(budget(90),build(1329,'infrastructure'),rd(2)),'construct_infrastructure'),
('field_repair','Field Repair and Recovery','Train repair teams and establish contracts for returning damaged equipment to service. This will improve logistical efficiency without supplying equipment that Estonia has not bought.',reward(budget(45),idea('field_repair_network'),xp(15)),'production'),
('air_defence_sites','Prepared Air Defence Sites','Prepare permanent air defence infrastructure near Tallinn. The sites help protect vital facilities, but Estonia still needs equipment, trained crews and allied air support.',reward(budget(80),build(13,'anti_air_building',2),rd(3)),'air_fighter'),
('national_supply_plan','The National Supply Plan','Unify military logistics with municipal and commercial distribution arrangements. Clear priorities will reduce avoidable consumption under wartime pressure.',reward(budget(25),rd(4),idea('joint_logistics')),'army_motorized')]),
('partners',[('allied_liaison','Permanent Allied Liaison','Maintain working relationships with allied commands and diplomatic services. Estonia’s forces need compatible plans rather than an assumption that foreign aid will arrive automatically.',reward(pp(45),rd(2)),'alliance'),
('interoperability','Interoperable Communications','Fund compatible communications and train staff in allied procedures. Equipment and doctrine should help Estonian units operate alongside larger partners.',reward(budget(50),rd(4),xp(15)),'intelligence_exchange'),
('allied_receiving','Receive Allied Forces','Plan the movement, basing and support of visiting forces with local authorities. This complements existing NATO reinforcement arrangements and never creates a duplicate allied army.',reward(budget(55),rd(4),xp(10)),'military_deal'),
('realistic_procurement','Procurement We Can Sustain','Choose maintainable equipment, verify suppliers and train crews before increasing commitments. Make paid procurement decisions available instead of issuing unlimited free stocks.',reward(pp(40),flag('procurement_plan'),'custom_effect_tooltip = TFR_EST_procurement_plan_tt'),'small_arms'),
('air_warning','Integrated Air Warning','Improve the infrastructure used to detect and report air threats. Warning is useful even when Estonia must rely on allied aircraft for interception.',reward(budget(70),build(13,'radar_station'),rd(3)),'radar'),
('prepared_alliance','A Prepared Member of the Alliance','Complete a practical allied support plan and exercise the command arrangements. Estonia retains responsibility for its defence while using collective strength effectively.',reward(rd(4),xp(20),flag('alliance_prepared')),'major_alliance')])]
for col,(name,nodes) in enumerate(military):
    previous='opening_marriage_referendum'
    for row,(s,title,desc,eff,icon) in enumerate(nodes):
        F(s,title,desc,33+col*3,row+2,previous,eff,icon,priority=15 if row<3 else 10)
        previous=s

F('prepared_positions','Prepared Defensive Positions','Defensive works around Tallinn and Narva can buy time for mobilization and allied action. Fund modest permanent positions in provinces Estonia owns and controls; the works remain useful only with trained forces and functioning supply.',33,8,'total_defence',reward(budget(60),fort(13,3152),fort(840,4640),rd(3)),'fortify_city',priority=10)
F('artillery_observers','Artillery Observation and Coordination','Estonia’s artillery must make limited equipment count. Train observers, improve communications and rehearse coordination with infantry and allied fire support. This focus grants experience and readiness; equipment must still be produced or procured.',36,8,'national_supply_plan',reward(budget(40),xp(25),rd(3)),'army_artillery',priority=10)
F('air_defence_integration','Integrate Air Defence and Warning','Air warning, prepared sites and allied liaison need one reporting procedure. Train crews and command staff around realistic limits, so a small air defence network can support civilian protection and military movement.',39,8,'prepared_alliance',reward(budget(45),'air_experience = 20',rd(3)),'air_doctrine',priority=10)

first = [
('first_emergency','The First European War','The first continental war has reached Estonia’s campaign. Convene the emergency cabinet, maintain the constitutional chain of authority and put existing preparedness plans into operation.',reward(co(3),rd(3),event(30)),'major_war'),
('first_civil_protection','Protect the Civilian Population','Coordinate shelters, hospitals and evacuation routes with the needs of the field army. Clear information will reduce panic and keep essential services operating.',reward(budget(50),co(4),rd(2)),'consumer_goods'),
('first_reserve_call','Put the Reserve Plan into Effect','Open the recruitment plan for additional reserve formations. Equipment and manpower remain real constraints, while readiness determines how quickly those units can be organized.',reward(flag('reserve_plan'),'if = { limit = { TFR_EST_can_mobilize = yes } TFR_EST_mobilize_reserves = yes }'),'army_doctrines'),
('first_command','An Emergency Joint Staff','Reduce delays between army headquarters, Kaitseliit and civilian authorities. The staff must coordinate defence while keeping responsibility for political decisions with the cabinet.',reward(xp(25),rd(4)),'defence'),
('first_supply','Keep the Supply Routes Open','Move maintenance teams, reserve transport and essential stores according to wartime priorities. Sustained logistics can compensate for some disadvantages of size.',reward(budget(40),rd(3),idea('wartime_transport')),'army_motorized'),
('first_allied_staff','The Allied Staff Network','Keep liaison officers connected to functioning allied commands. Joint procedures and reliable reporting can make outside support useful without assuming any particular ally will survive.',reward(xp(20),rd(3)),'alliance'),
('first_emergency_laws','Emergency Laws with a Mandate','Parliament must decide how far emergency authority extends and when it will be reviewed. Discipline and legitimacy both matter while the republic fights for survival.',reward(pp(40),event(31)),'political_pressure'),
('first_defend_capital','Defend the Capital’s Institutions','Disperse vital records and organize the protection of national institutions. Even if Tallinn becomes a battlefield, lawful authority and public communication must continue.',reward(budget(40),co(3),rd(3)),'fortify_city'),
('first_endurance','A Small State Can Endure','Coordinate relief for displaced people, rest rotations and the repair of essential services. Estonia’s war effort must remain sustainable beyond the opening emergency.',reward(co(4),idea('national_endurance')),'national_unity'),
('first_lessons','Record the First War’s Lessons','Collect evidence from military operations and civilian administration before experience is lost. Preparation for recovery and future threats starts while the lessons are fresh.',reward(xp(30),rd(4),flag('first_lessons')),'army_doctrines')]
previous='opening_marriage_referendum'
for row,(s,title,desc,eff,icon) in enumerate(first):
    F(s,title,desc,3,row+18,previous,eff,icon,cost=3,avail='has_country_flag = TFR_EST_first_war_seen',priority=40)
    previous=s

interwar = [
('reconstruction_audit','Assess the Damage','The first war’s settlement has changed the republic’s position. Count damaged services, industrial losses and displaced families before making promises about recovery.',reward(pp(50),event(40)),'construct_infrastructure'),
('reconstruction_services','Restore Essential Services','Repair the administrative links, healthcare provision and municipal services that keep daily life possible. Recovery must reach functioning Estonian territory, including a reduced republic.',reward(budget(60),co(5)),'consumer_goods'),
('returning_families','Help Families Rebuild','Assist displaced residents with documents, housing access and employment services. Recovery should reduce exclusion rather than creating a permanent division between returnees and those who stayed.',reward(budget(50),co(4)),'national_unity'),
('reconstruction_industry','Restart Civilian Production','Repair capacity and reliable infrastructure must precede new contracts. Invest in civilian manufacturing in the capital region where Estonia retains ownership and control.',reward(budget(180),build(13,'industrial_complex')),'construct_civ_factory'),
('reconstruction_accounts','Publish the Recovery Accounts','Emergency expenditure deserves scrutiny after the immediate crisis. Audit contracts and publish the debt commitment so recovery strengthens institutional trust.',reward(pp(35),co(4)),'political_pressure'),
('reconstruction_defence','Rebuild Defence on Evidence','Use wartime experience to revise training and maintenance plans. The new force must reflect available territory, manpower and equipment.',reward(budget(45),rd(5),xp(25)),'army_doctrines'),
('reconstruction_partners','Rebuild Working Partnerships','Re-establish practical diplomatic, trade and military links with governments that remain able to cooperate. Estonia should adapt to the settlement rather than relying on a vanished international order.',reward(pp(60),rd(2)),'alliance'),
('interwar_watch','Watch the Next Gathering Storm','The first settlement may not have ended Europe’s crisis. Keep contingency plans current while restoring ordinary politics and preparing to respond to another continental war.',reward(rd(4),co(3),flag('interwar_watch')),'defence')]
previous='opening_marriage_referendum'
for row,(s,title,desc,eff,icon) in enumerate(interwar):
    F(s,title,desc,9,row+18,previous,eff,icon,avail='check_variable = { TFR_EST_campaign_stage > 1 } has_war = no',priority=25)
    previous=s

second = [
('second_emergency','Europe at War Again','A second European war has begun. Activate the revised emergency plan and account for the political and territorial position inherited from the first settlement.',reward(co(3),rd(3),event(50)),'major_war'),
('second_readiness','Readiness Without Illusions','Review the force we can actually field, the stores we possess and the routes still available. Commitments must be based on current capacity rather than plans written before the first war.',reward(xp(25),rd(4)),'army_doctrines'),
('second_local_networks','Local Networks Under Pressure','Municipal authorities and trained volunteers can sustain services when national links are disrupted. Distribute clear responsibilities and emergency communications procedures.',reward(budget(40),co(4),rd(2)),'national_unity'),
('second_reserve_renewal','Renew the Reserve System','Update recruitment arrangements and refresh reserve training. The plan unlocks normal recruitment if not already established, while all equipment remains subject to supply.',reward(rd(3),flag('reserve_plan'),'if = { limit = { TFR_EST_can_mobilize = yes } TFR_EST_mobilize_reserves = yes }'),'army_doctrines'),
('second_maintenance','Keep the Army Serviceable','Fund field repair arrangements and prioritize compatible equipment. In a long war, recovering usable systems is often more realistic than replacing every loss with a new purchase.',reward(budget(65),xp(20),rd(3)),'production'),
('second_common_command','A Common Operational Picture','Coordinate reports, supply priorities and liaison with surviving partners. Clear information allows Estonia to contribute effectively without surrendering its command responsibilities.',reward(xp(25),rd(3)),'alliance'),
('second_constitution','Preserve the Republic’s Mandate','A second emergency must still answer to lawful political authority. Decide how to maintain scrutiny and public support under renewed pressure.',reward(pp(40),event(51)),'political_pressure'),
('second_supply_resilience','Supply Through Disruption','Apply the first war’s lessons to dispersed repair, transport and distribution. Fund a renewed logistics exercise tied to the territory we control.',reward(budget(50),rd(4),idea('second_war_logistics')),'army_motorized'),
('second_social_endurance','Endurance for Soldiers and Citizens','Support families, displaced residents and exhausted essential workers. A war effort that consumes the society it defends cannot last indefinitely.',reward(budget(55),co(5)),'consumer_goods'),
('second_republic_survives','Carry the Republic Through','Maintain lawful authority, functioning institutions and the means to continue after the second settlement. Survival gives Estonia the opportunity to recover its future.',reward(co(4),rd(3),flag('second_lessons')),'national_unity')]
previous='opening_marriage_referendum'
for row,(s,title,desc,eff,icon) in enumerate(second):
    F(s,title,desc,15,row+18,previous,eff,icon,cost=3,avail='has_country_flag = TFR_EST_second_war_seen',priority=45)
    previous=s

post = [
('second_settlement','After the Second Settlement','The second war has reached a settlement. The republic must assess its borders, partners and obligations before rebuilding the institutions that can serve its people.',reward(co(3),pp(60),event(60)),'alliance'),
('postwar_repairs','Repair the Republic Again','Restore transport and public services around Tallinn where the state retains control. Recovery requires a funded commitment, even when political attention turns elsewhere.',reward(budget(100),build(13,'infrastructure'),co(3)),'construct_infrastructure'),
('postwar_industry','Industry for Recovery','Support a durable civilian production base in Northern Estonia. New capacity should serve employment and essential goods before ambitious military projects.',reward(budget(200),build(13,'industrial_complex')),'construct_civ_factory'),
('postwar_accountability','Accountability After Emergency','Bring exceptional powers and contracts back before parliament. A state that survived war must recover the ordinary rights and oversight that give survival meaning.',reward(co(5),pp(40)),'political_pressure'),
('postwar_security','A Sustainable Security Policy','Maintain trained forces and a credible reserve plan within the resources of the surviving republic. End emergency habits that no longer contribute to defence.',reward(xp(25),rd(4),idea('sustainable_security')),'defence'),
('postwar_future','Estonia Has a Future','Conclude the two-war campaign with a programme of lawful government, viable services and realistic security. The next generation deserves institutions capable of managing peace.',reward(co(5),pp(100),flag('campaign_complete')),'national_unity')]
previous='opening_marriage_referendum'
for row,(s,title,desc,eff,icon) in enumerate(post):
    F(s,title,desc,21,row+18,previous,eff,icon,avail='check_variable = { TFR_EST_campaign_stage > 3 } has_war = no',priority=30)
    previous=s

restoration = [
('restored_authority','Independent Authority Restored','An occupation has ended and Estonia once again controls its own government. The first task is to identify lawful authority, restore records and prepare the election that will give the cabinet a fresh mandate.',reward(co(3),pp(60),event(70)),'national_unity'),
('restore_civic_rights','Restore Civic Rights','Reopen civic organizations, independent public debate and fair access to administration. Restoration should apply clear legal standards rather than private revenge.',reward(budget(25),co(5)),'political_pressure'),
('review_occupation_records','Review Occupation Records','Investigate abuses through lawful procedures and preserve evidence. Distinguish coerced survival from deliberate wrongdoing so accountability can strengthen trust.',reward(co(4),event(71)),'intelligence_exchange'),
('restore_local_services','Restore Local Services','Rebuild the municipal staff and service arrangements weakened during occupation. Target resources at territory the independent state actually controls.',reward(budget(50),co(4),rd(2)),'consumer_goods'),
('restore_defence_command','Reconstitute the Defence Command','Review personnel, training and equipment before re-establishing military responsibilities. Retain useful skills while restoring accountable national command.',reward(budget(40),rd(4),xp(20)),'army_doctrines'),
('restoration_compact','A Restoration Compact','Bring government, opposition and municipalities together around the restored constitutional order. Elections and practical recovery must give the republic a future beyond the occupation’s divisions.',reward(co(5),pp(60),flag('restoration_compact')),'national_unity')]
previous='opening_marriage_referendum'
for row,(s,title,desc,eff,icon) in enumerate(restoration):
    F(s,title,desc,27,row+18,previous,eff,icon,avail='has_country_flag = TFR_EST_restoration_pending',priority=35)
    previous=s

tree='''# Persistent tree: completed policies survive elections and campaign handoffs.
focus_tree = {
    id = TFR_EST_main_tree
    country = { factor = 0 modifier = { add = 100 original_tag = EST NOT = { has_country_flag = TFR_EST_occupied } } }
    default = no
    initial_show_position = { focus = TFR_EST_opening_kose_voobu }
'''+''.join(f'    shared_focus = TFR_EST_opening_{policy.suffix}\n' for policy in POLICIES)+''.join(f'    shared_focus = TFR_EST_ratas_{policy.suffix}\n' for policy in RATAS_POLICIES)+''.join(f'    shared_focus = TFR_EST_kallas_{policy.suffix}\n' for policy in KALLAS_POLICIES)+''.join(f[1] for f in focuses)+'}\n'

ideas={
'government_continuity':('Government Continuity','Secure communications, administrative backups and remote procedures keep government functioning when ordinary meetings are disrupted.','political_power_gain = 0.05'),
'open_administration':('Open Administration','Public information and procurement scrutiny give emergency decisions a stronger foundation of trust.','stability_factor = 0.03'),
'secure_digital_state':('Secure Digital State','Protected records and rehearsed recovery procedures improve the efficiency of public administration.','political_power_gain = 0.04'),
'research_partnerships':('Practical Research Partnerships','Estonian researchers and employers share a programme focused on useful, maintainable capabilities.','research_speed_factor = 0.03'),
'maintenance_network':('National Maintenance Network','Common tools, skills and repair contracts improve the value of limited industrial capacity.','production_factory_efficiency_gain_factor = 0.04'),
'kaitseliit_network':('Kaitseliit Training Network','Common instructor standards help local volunteer units support coherent national defence plans.','training_time_army_factor = -0.03'),
'total_defence':('Total Defence Plan','Clear responsibilities link the regular force, reserves, Defence League and municipal services.','army_defence_factor = 0.03\narmy_org_factor = 0.02'),
'field_repair_network':('Field Repair Network','Recovery teams and repair contracts reduce avoidable equipment losses in service.','attrition = -0.03'),
'joint_logistics':('Joint Logistics Plan','Military supply priorities are coordinated with municipalities and commercial transport.','supply_consumption_factor = -0.03'),
'wartime_transport':('Wartime Transport Priorities','Temporary distribution arrangements sustain forces and essential services during the European wars.','supply_consumption_factor = -0.02'),
'national_endurance':('National Endurance','Relief and service continuity help the republic sustain an extended national emergency.','war_support_factor = 0.03'),
'second_war_logistics':('Second-War Logistics','The first war’s experience informs dispersed repair, distribution and transport priorities.','supply_consumption_factor = -0.02'),
'sustainable_security':('Sustainable National Security','Training and realistic procurement support a force the surviving republic can maintain.','army_org_factor = 0.02'),
'pandemic_support':('Public Health Support','A funded public health response protects essential services and vulnerable households.','stability_factor = 0.03'),
'rights_review':('Emergency Rights Review','Regular scrutiny limits emergency powers to their stated purposes.','stability_factor = 0.02'),
'emergency_authority':('Temporary Emergency Authority','Rapid procedures improve administrative action but create an obligation to restore normal oversight.','political_power_gain = 0.08\nstability_factor = -0.02'),
'centre_cabinet':('Keskerakond Governing Programme','Local investment and accountable social provision support a broad governing coalition. Active only while a confirmed Keskerakond government leads the country.','stability_factor = 0.03\npolitical_power_gain = 0.05'),
'reform_cabinet':('Reform Governing Programme','Secure services and investment discipline improve the capacity of an open state. Active only while a confirmed Reform government leads the country.','research_speed_factor = 0.02\nproduction_speed_buildings_factor = 0.03'),
'ekre_cabinet':('EKRE Governing Programme','Local organization and domestic preparedness support national defence. Active only while a confirmed EKRE government leads the country.','mobilization_speed = 0.05\narmy_defence_factor = 0.03'),
'isamaa_cabinet':('Isamaa Governing Programme','National institutions and territorial defence reinforce constitutional continuity. Active only while a confirmed Isamaa government leads the country.','stability_factor = 0.02\narmy_org_factor = 0.03'),
'sde_cabinet':('Social Democratic Governing Programme','Accessible services and negotiated emergency arrangements strengthen social resilience. Active only while a confirmed Social Democratic government leads the country.','stability_factor = 0.04\nwar_support_factor = 0.02'),
'e200_cabinet':('Eesti 200 Governing Programme','Education and institutional reform support a measured long-term development programme. Active only while a confirmed Eesti 200 government leads the country.','research_speed_factor = 0.03\npolitical_power_gain = 0.04'),
'pp_cabinet':('Parempoolsed Governing Programme','Disciplined contracts and competent administration support productive enterprise. Active only while a confirmed Parempoolsed government leads the country.','production_speed_buildings_factor = 0.04\nproduction_factory_efficiency_gain_factor = 0.03'),
}
ideas_text='ideas = { country = {\n'
for s,(name,desc,mods) in ideas.items():
    L(P+s,name); L(P+s+'_desc',desc)
    ideas_text+=f'{P+s} = {{ picture = generic_military_org removal_cost = -1 allowed = {{ original_tag = EST }} allowed_civil_war = {{ always = yes }} modifier = {{ {mods} }} }}\n'
ideas_text+='} }\n'

L('TFR_EST_reserve_plan_tt','Unlocks the reserve mobilization decision. Recruitment uses normal manpower, equipment and training; no free equipped divisions are created. Requires readiness of at least 50 or an active war, independence and control of Northern Estonia.')
L('TFR_EST_procurement_plan_tt','Unlocks paid domestic procurement decisions. Each contract is limited by a cooldown and adds public debt through TFR’s economic ledger.')

# Explicit choices develop domestic and wartime conflicts without selecting a different political route.
events = [
(1,'The Republic in 2020','The cabinet meets in Tallinn with a majority of 57 seats: Keskerakond, EKRE and Isamaa. Across the chamber stand Reform and the Social Democrats; Eesti 200 seeks a place in parliament. President Kersti Kaljulaid remains a distinct constitutional authority.\n\nAs international stability deteriorates, coalition disagreements cannot obscure the practical task of keeping the republic capable of governing.','generic_handshake',[
('A workable coalition and an accountable parliament.',reward(co(2),pp(25)),70),
('Begin with a wider consultation.',reward(co(4),pp(-25)),30)]),
(2,'The Public Health Response','Hospital administrators, employers and municipal leaders warn that an epidemic could interrupt daily life and exhaust essential services. The cabinet can fund broad support or concentrate on immediate capacity. Both require visible expenditure and a clear plan for reviewing exceptional measures.','generic_research_lab',[
('Support health services and vulnerable households.',reward(budget(75),co(5),idea('pandemic_support')),65),
('Fund immediate capacity and preserve flexibility.',reward(budget(35),co(2),pp(25)),35)]),
(3,'Distinct Responsibilities','The president and prime minister discuss how emergency measures will be reviewed. The cabinet directs policy; the president must remain able to assess constitutional questions and represent the republic. Cooperation works best when those distinct responsibilities are explicit.','generic_sign_treaty1',[
('Publish a constitutional consultation protocol.',reward(co(4),pp(-20)),75),
('Rely on existing procedures and regular meetings.',reward(co(2),pp(15)),25)]),
(10,'Integration Through Participation','Local leaders in Ida-Viru ask whether civic integration will bring practical opportunities or another set of political slogans. Language education and trusted local institutions can strengthen a shared republic, but progress demands a sustained commitment.','generic_rally',[
('Fund language access and local civic projects.',reward(budget(30),co(4)),65),
('Prioritize employment-linked language training.',reward(budget(20),co(2),pp(20)),35)]),
(11,'The Cost of Budget Discipline','The review of public spending has found duplication, but not every disputed service is unnecessary. Reform’s ministers must choose how much immediate consolidation to impose while schools and municipal authorities prepare for a wider crisis.','generic_read_write',[
('Phase savings and protect essential local services.',reward(budget(25),co(3),pp(-20)),65),
('Implement the consolidation promptly.',reward(co(-4),pp(60)),35)]),
(12,'Sovereignty and Practical Cooperation','EKRE ministers want external commitments tested against Estonia’s sovereignty. Diplomats reply that cooperation provides protection and influence precisely because Estonia cannot act alone. The cabinet must decide how to present its review without closing useful channels.','generic_sign_treaty2',[
('Demand clear safeguards through negotiation.',reward(co(2),rd(2),pp(10)),70),
('Confront partners publicly.',reward(co(-3),pp(60),rd(-2)),30)]),
(13,'Energy and Livelihoods','Isamaa’s energy review identifies vulnerabilities alongside local jobs that depend on the current system. Rapid transition promises resilience but creates immediate social costs. A staged approach preserves jobs while taking longer to reduce exposure.','generic_factory',[
('Fund a staged transition and worker support.',reward(budget(65),co(4),rd(2)),65),
('Accelerate resilience investment.',reward(budget(85),co(-2),rd(5)),35)]),
(14,'Paying for Public Services','The Social Democratic cabinet has promised dependable healthcare, fair work and civil preparedness. Parliament now asks how these commitments will be funded. Honest choices can preserve trust even when no option is painless.','generic_read_write',[
('Phase the programme with transparent financing.',reward(budget(40),co(3),pp(-20)),65),
('Deliver the expansion immediately.',reward(budget(100),co(5),pp(-40)),35)]),
(15,'The Pace of Institutional Reform','Eesti 200’s proposals would consolidate administrative responsibilities. Local authorities warn that rapid changes may remove expertise and accessible services. The government must turn long-term ambition into a pace institutions can actually sustain.','generic_read_write',[
('Pilot the reform and publish results.',reward(budget(30),co(3)),70),
('Proceed quickly with a national reorganization.',reward(pp(50),co(-3)),30)]),
(16,'Restraint and Public Confidence','Parempoolsed argues that disciplined spending protects future choices. Municipal representatives fear that abrupt cuts will make essential services unreliable. The new cabinet must decide what fiscal discipline means in practice.','generic_read_write',[
('Protect essentials and consolidate in stages.',reward(budget(25),co(3),pp(-20)),65),
('Apply an immediate expenditure review.',reward(pp(55),co(-4)),35)]),
(17,'A Governing Programme Enacted','Parliament has carried a full governing programme into law. The reforms become part of Estonia’s political history. Administrative coordination associated with this programme remains strongest while its party leads a confirmed cabinet; a future election can bring another programme into office.','generic_sign_treaty1',[
('Invite scrutiny of the programme’s results.',reward(co(3),pp(25)),70),
('Concentrate on implementation.',reward(rd(2),pp(40)),30)]),
(20,'A Digital State and Its Citizens','More public services now depend on connected records. Officials want broad access during emergencies, while civic groups ask for independent review of how that power is used. Security and public trust require practical rules rather than absolute promises.','generic_research_lab',[
('Publish access rules and support independent review.',reward(budget(15),co(4)),75),
('Expand emergency access under cabinet supervision.',reward(pp(50),co(-3),rd(1)),25)]),
(30,'The Emergency Cabinet Convenes','War has reached Estonia’s campaign. Ministers receive reports on mobilization, civilian services and allied operations. The government must give the public a clear account of what it can do and where it depends on partners.','generic_army',[
('Explain the situation and preserve scrutiny.',reward(co(4),pp(-20)),65),
('Concentrate emergency authority in the cabinet.',reward(pp(60),co(-2)),35)]),
(31,'Emergency Powers Before Parliament','The emergency bill provides faster procurement, requisitioning and movement controls. Its supporters warn against delay; critics insist that expiry dates and compensation are essential to legitimacy. Parliament must choose the form of authority it grants.','generic_read_write',[
('Grant powers with scheduled parliamentary review.',reward(co(4),'add_timed_idea = { idea = TFR_EST_rights_review days = 180 }'),65),
('Grant broader temporary executive authority.',reward(co(-3),'add_timed_idea = { idea = TFR_EST_emergency_authority days = 180 }'),35)]),
(40,'The First Settlement','The first European war has ended for the current campaign stage. Its settlement has reshaped borders and alliances. Estonia must assess the resources it still controls and decide whether recovery begins with household security or the productive base.','generic_ruins',[
('Restore household and municipal services first.',reward(budget(55),co(5)),55),
('Prioritize productive infrastructure and logistics.',reward(budget(65),rd(4),co(1)),45)]),
(50,'A Second European Emergency','The continent is at war again. The first conflict’s lessons remain useful, but forces, partners and territory may have changed. The cabinet must organize a new response around what Estonia can actually sustain.','generic_army',[
('Build a broad emergency consensus.',reward(co(4),pp(-20)),65),
('Give the emergency staff a rapid mandate.',reward(pp(50),rd(2),co(-2)),35)]),
(51,'The Constitution Through a Second War','A renewed emergency has tested the patience of parliament and the public. Officials ask for faster authority while civic organizations warn that repeated exceptions may become permanent. The republic needs a decision that can endure scrutiny after the fighting.','generic_read_write',[
('Retain review and clear expiry dates.',reward(co(4),'add_timed_idea = { idea = TFR_EST_rights_review days = 180 }'),70),
('Renew temporary broad cabinet powers.',reward(co(-3),'add_timed_idea = { idea = TFR_EST_emergency_authority days = 180 }'),30)]),
(60,'Beyond the Second War','The second settlement has left Estonia with a changed European environment. The country’s survival creates an opportunity to restore ordinary government and a sustainable economy. A durable future now matters more than emergency prestige.','generic_sign_treaty2',[
('Restore civic life and account for emergency powers.',reward(co(5),'remove_ideas = TFR_EST_wartime_transport\nremove_ideas = TFR_EST_second_war_logistics'),70),
('Begin with security and reconstruction planning.',reward(rd(3),pp(40)),30)]),
(70,'The Republic Governs Itself Again','Occupation has ended. Civil servants recover files, communities reopen organizations and political parties prepare to compete openly. The independence settlement brings its own uncertainties, but authority can now return to a constitutional mandate.','generic_rally',[
('Rebuild lawful institutions and prepare elections.',reward(co(5),pp(-20)),75),
('Prioritize immediate administrative continuity.',reward(pp(50),co(2)),25)]),
(71,'Justice After Occupation','Occupation records contain evidence of coercion, collaboration and abuses. Families demand accountability, while officials warn against accusations becoming private retaliation. The restored republic must choose a process worthy of its laws.','generic_read_write',[
('Use independent courts and publish clear standards.',reward(budget(25),co(5)),75),
('Prioritize a limited review of documented abuses.',reward(co(2),pp(25)),25)]),
]

# A cabinet that enters either war receives its own political response once.
# Later governments may receive their own response, while completed policies remain intact.
war_responses = {
'centre': (
 ('A Broad Social Defence', 'Keskerakond ministers emphasize that a government cannot mobilize society without protecting the households that carry its burdens. Coalition partners favor concentrating resources on immediate military requirements. The cabinet must choose how to present its first-war programme.',
  ('Protect families and municipal services.', reward(budget(40),co(5)), 65),
  ('Prioritize reserve administration and supply.', reward(budget(25),rd(4),co(1)), 35)),
 ('Keskerakond in the Second Emergency', 'The second war arrives after Estonia has already endured a continental settlement. Keskerakond’s cabinet can renew a broad social compact or put its limited resources into recovering practical defence capacity. Both choices demand cooperation beyond the party itself.',
  ('Renew the social compact for service families.', reward(budget(45),co(5)), 60),
  ('Fund reserve recovery and municipal logistics.', reward(budget(35),rd(4),xp(10)), 40))),
'reform': (
 ('Competence Under Fire', 'Reform’s cabinet argues that accurate information and disciplined procurement are essential in the first war. Parliament also needs to know whether emergency efficiency will come with protection for citizens excluded from digital services.',
  ('Keep services accessible and publish commitments.', reward(budget(30),co(4),pp(-10)), 60),
  ('Prioritize command and procurement efficiency.', reward(budget(25),rd(4),xp(10)), 40)),
 ('Reform Faces Another War', 'The second war tests Reform’s commitment to openness and sustainable administration. Ministers debate whether to fund additional service access or concentrate the next tranche of emergency spending on interoperable defence planning.',
  ('Protect transparent and accessible public services.', reward(budget(35),co(5)), 55),
  ('Fund interoperable command and maintenance.', reward(budget(40),rd(4),xp(15)), 45))),
'ekre': (
 ('National Mobilization and Allied Support', 'EKRE’s first-war cabinet must turn sovereignty into practical survival. Local organization gives the state reach, while allied liaison offers capabilities Estonia cannot supply alone. Political rhetoric now has to serve a workable defence plan.',
  ('Put county volunteers and civil duty first.', reward(budget(30),rd(3),co(3)), 55),
  ('Prioritize practical allied military coordination.', reward(rd(4),xp(15),pp(-15)), 45)),
 ('Sovereignty Through a Second War', 'After one European settlement, EKRE must assess what independence requires in another war. A domestic mobilization campaign can rally supporters; cooperation with surviving partners can improve the force’s practical effectiveness.',
  ('Renew domestic preparedness with local guarantees.', reward(budget(40),rd(4),co(2)), 55),
  ('Reaffirm allied cooperation under Estonian command.', reward(rd(3),xp(20),co(2)), 45))),
'isamaa': (
 ('Institutions in the First War', 'Isamaa’s cabinet treats the continuity of national institutions as a defence responsibility. The army wants clearer territorial plans, while municipal leaders ask that legal authority and essential services remain accessible if Tallinn is disrupted.',
  ('Protect constitutional and local continuity.', reward(budget(25),co(4),rd(1)), 60),
  ('Concentrate on territorial command exercises.', reward(budget(30),rd(4),xp(10)), 40)),
 ('The Nation Across Two Wars', 'Isamaa faces another emergency with institutions already tested by the first war. Its ministers can fund civilian continuity across counties or renew territorial defence planning around the republic’s current borders.',
  ('Keep county institutions and family services working.', reward(budget(35),co(5)), 60),
  ('Review territorial defence against the present map.', reward(budget(30),rd(4),xp(15)), 40))),
'sde': (
 ('Solidarity in the First War', 'The Social Democratic cabinet argues that civil resilience and fair emergency work protect the war effort. Military officers ask for reliable service-family arrangements, while local authorities warn that healthcare and relief cannot absorb every new duty.',
  ('Fund relief and essential public services.', reward(budget(45),co(5)), 65),
  ('Prioritize reservist families and emergency work.', reward(budget(30),rd(3),co(3)), 35)),
 ('Solidarity Under Renewed Pressure', 'A second war brings exhausted services and households into another national emergency. The Social Democrats must decide how to distribute limited support between immediate civilian needs and the practical arrangements that sustain mobilization.',
  ('Renew household relief and healthcare support.', reward(budget(55),co(5)), 65),
  ('Fund service families and civil logistics.', reward(budget(40),rd(3),co(3)), 35))),
'e200': (
 ('Long-Term Plans Meet the First War', 'Eesti 200’s cabinet must adapt plans written for gradual reform to the urgency of war. It can preserve education and administrative continuity or give its review teams a more immediate role in defence coordination.',
  ('Protect schools and administrative continuity.', reward(budget(35),co(4),rd(1)), 55),
  ('Apply the review programme to defence coordination.', reward(budget(25),rd(4),xp(10)), 45)),
 ('A Future Beyond the Second War', 'Eesti 200’s long-term ambitions have survived one settlement and now face another war. Reconstruction planning can keep future institutions viable, but the immediate field force also needs adaptable maintenance and training arrangements.',
  ('Keep education and recovery planning alive.', reward(budget(40),co(5),pp(10)), 55),
  ('Prioritize adaptable training and field repair.', reward(budget(35),rd(4),xp(15)), 45))),
'pp': (
 ('Discipline During the First War', 'Parempoolsed’s cabinet must apply fiscal and procurement discipline to a national emergency. Immediate checks can prevent waste, while service guarantees protect confidence in a government still proving its ability to lead.',
  ('Audit contracts while protecting essential services.', reward(budget(20),co(4),pp(-10)), 60),
  ('Concentrate on procurement and maintenance costs.', reward(budget(25),rd(4),xp(10)), 40)),
 ('A Reliable State in the Second War', 'The second war tests Parempoolsed’s argument that a disciplined state can preserve resources for crisis. The cabinet can strengthen public accountability or concentrate new expenditure on maintaining the force already available.',
  ('Keep emergency contracts open to scrutiny.', reward(budget(20),co(5),pp(-10)), 60),
  ('Fund maintainable equipment and reserve planning.', reward(budget(35),rd(4),xp(15)), 40)))
}
for suffix,pid,label in parties:
    for war,details in enumerate(war_responses[suffix],1):
        title,desc,*options = details
        events.append((80+pid if war==1 else 90+pid,title,desc,'generic_army',options))

events_text='add_namespace = tfr_estonia_content\n\n'
for num,title,desc,pic,options in events:
    key=f'tfr_estonia_content.{num}'
    L(key+'.t',title); L(key+'.d',desc)
    events_text+=f'country_event = {{\n id = {key}\n title = {key}.t\n desc = {key}.d\n picture = GFX_report_event_{pic}\n is_triggered_only = yes\n trigger = {{ original_tag = EST NOT = {{ has_country_flag = TFR_EST_occupied }} }}\n'
    for i,(name,eff,weight) in enumerate(options):
        opt=key+'.'+chr(97+i);L(opt,name)
        events_text+=f' option = {{ name = {opt} ai_chance = {{ factor = {weight} }} {eff} }}\n'
    events_text+='}\n\n'

# Weekly programme reconciliation is repeat-safe and never pays completion rewards twice.
effects='''TFR_EST_refresh_programme = {
'''
for suffix,pid,label in parties:
    effects+=f'''if = {{
 limit = {{ check_variable = {{ TFR_EST_pm_party = {pid} }} has_country_flag = TFR_EST_{suffix}_programme NOT = {{ has_country_flag = TFR_EST_occupied }} NOT = {{ has_country_flag = TFR_EST_caretaker }} }}
 if = {{ limit = {{ NOT = {{ has_idea = TFR_EST_{suffix}_cabinet }} }} add_ideas = TFR_EST_{suffix}_cabinet }}
}} else = {{ if = {{ limit = {{ has_idea = TFR_EST_{suffix}_cabinet }} remove_ideas = TFR_EST_{suffix}_cabinet }} }}
'''
effects+='}\n\nTFR_EST_content_tick = {\n TFR_EST_refresh_programme = yes\n'
effects+=''' if = {
  limit = { OR = { has_country_flag = TFR_EST_occupied check_variable = { TFR_EST_campaign_stage > 3 } } }
  remove_ideas = TFR_EST_wartime_transport
  remove_ideas = TFR_EST_second_war_logistics
 }
 if = {
  limit = { date > 2021.1.1 }
  remove_ideas = TFR_EST_pandemic_support
 }
'''
for suffix,pid,label in parties:
    for war,stage in ((1,1),(2,3)):
        eid=80+pid if war==1 else 90+pid
        effects+=f''' if = {{
 limit = {{ check_variable = {{ TFR_EST_campaign_stage = {stage} }} check_variable = {{ TFR_EST_pm_party = {pid} }} NOT = {{ has_country_flag = TFR_EST_occupied }} NOT = {{ has_country_flag = TFR_EST_caretaker }} NOT = {{ has_country_flag = TFR_EST_{suffix}_war{war}_response }} }}
 set_country_flag = TFR_EST_{suffix}_war{war}_response
 country_event = {{ id = tfr_estonia_content.{eid} }}
 }}\n'''
effects+='}\n'

categories='''TFR_EST_national_programmes = {
 icon = generic_economy
 priority = 85
 allowed = { original_tag = EST }
 visible = { NOT = { has_country_flag = TFR_EST_occupied } }
 visible_when_empty = yes
}
TFR_EST_defence_programmes = {
 icon = army_reform
 priority = 84
 allowed = { original_tag = EST }
 visible = { NOT = { has_country_flag = TFR_EST_occupied } }
 visible_when_empty = yes
}
'''
L('TFR_EST_national_programmes','National Programmes')
L('TFR_EST_national_programmes_desc','Fund domestic policy and administrative work between major reforms. Expenditure adds debt through TFR’s economic ledger. Completed reforms persist after elections; cabinet programme benefits follow the current confirmed government.')
L('TFR_EST_defence_programmes','Defence Preparedness')
L('TFR_EST_defence_programmes_desc','Readiness supports reserve organization, training and logistics. Mobilization unlocks a recruitment template and training arrangements; units must still be trained with normal manpower and equipment. Allied reinforcement decisions remain governed by TFR.')
decisions={ 'TFR_EST_national_programmes':[], 'TFR_EST_defence_programmes':[] }

def D(category,s,title,desc,eff,cost=35,cooldown=180,available='',visible='',icon='generic_civil_support',ai=1,fire_once=False):
    ident=P+s;L(ident,title);L(ident+'_desc',desc)
    condition='NOT = { has_country_flag = TFR_EST_occupied }'
    decisions[category].append(f''' {ident} = {{
 icon = {'generic_military' if icon == 'generic_prepare_civil_war' else icon}
 cost = {cost}
 days_re_enable = {cooldown}
 {'fire_only_once = yes' if fire_once else ''}
 visible = {{ {condition} {visible} }}
 available = {{ {condition} {available} }}
 complete_effect = {{ {eff} }}
 ai_will_do = {{ factor = {ai} }}
 }}\n''')

D('TFR_EST_national_programmes','municipal_roundtable','Convene a Municipal Roundtable','Bring mayors and service administrators together to resolve practical access problems. Costs 35 political power and €15 million in public debt; increases cohesion by 2. Available every 180 days.',reward(budget(15),co(2)),available='NOT = { has_country_flag = TFR_EST_caretaker }',ai=2)
D('TFR_EST_national_programmes','publish_accounts','Publish Programme Accounts','Open public expenditure and implementation data to independent review. Costs 30 political power; increases cohesion by 1. Available every 180 days.',co(1),cost=30,ai=2)
D('TFR_EST_national_programmes','service_rehearsal','Rehearse Essential Service Continuity','Test municipal communications, records and staffing arrangements. Costs 40 political power and €20 million in public debt; increases readiness by 2 and cohesion by 1. Available every 180 days.',reward(budget(20),rd(2),co(1)),cost=40,available='has_country_flag = TFR_EST_done_opening_covid_emergency',ai=2)
D('TFR_EST_national_programmes','regional_training','Fund Regional Technical Training','Support vocational training linked to local employers. Costs 35 political power and €30 million in public debt; increases cohesion by 2 and grants 5 army experience through maintenance training. Available every 365 days.',reward(budget(30),co(2),xp(5)),cooldown=365,available='has_completed_focus = TFR_EST_technical_training',ai=1)
for suffix,pid,label in parties:
    D('TFR_EST_national_programmes',suffix+'_public_meetings',f'{label}: Public Programme Meetings',f'Explain the governing programme and hear local objections. Costs 40 political power and €10 million in public debt; increases cohesion by 1 and shifts polling support through the party campaign system. Requires a confirmed {label} government. Available every 180 days.',reward(budget(10),co(1),f'TFR_EST_campaign_{suffix} = yes'),cost=40,available=f'check_variable = {{ TFR_EST_pm_party = {pid} }} NOT = {{ has_country_flag = TFR_EST_caretaker }}',visible=f'check_variable = {{ TFR_EST_pm_party = {pid} }}',ai=1)
D('TFR_EST_defence_programmes','reserve_mobilization','Activate Reserve Recruitment','Unlock a reserve recruitment template and a limited training programme once. Costs 50 political power. Requires the reserve plan, readiness of at least 50 or an active war, independence and control of Northern Estonia. Recruit divisions normally; this decision does not create free manpower or equipment.','TFR_EST_mobilize_reserves = yes',cost=50,available='has_country_flag = TFR_EST_reserve_plan TFR_EST_can_mobilize = yes',visible='has_country_flag = TFR_EST_reserve_plan NOT = { has_country_flag = TFR_EST_reserves_mobilized }',icon='generic_prepare_civil_war',ai=5,fire_once=True)
D('TFR_EST_defence_programmes','readiness_exercise','Conduct a Readiness Exercise','Rehearse movement, issue procedures and command communications. Costs 45 political power and €30 million in public debt; increases readiness by 3 and grants 8 army experience. Available every 180 days.',reward(budget(30),rd(3),xp(8)),cost=45,available='has_completed_focus = TFR_EST_reserve_register check_variable = { TFR_EST_readiness < 90 }',icon='generic_prepare_civil_war',ai=3)
D('TFR_EST_defence_programmes','volunteer_training','Train Local Civil Defence Volunteers','Fund first aid, emergency communication and distribution exercises. Costs 35 political power and €15 million in public debt; increases readiness by 2 and cohesion by 1. Available every 180 days.',reward(budget(15),rd(2),co(1)),available='has_completed_focus = TFR_EST_kaitseliit_training',icon='generic_prepare_civil_war',ai=2)
D('TFR_EST_defence_programmes','lift_nato_restrictions','Activate the National Defence Mandate','Replace Estonia’s inherited peacetime NATO military restrictions through the national mobilization transition. Costs 50 political power. Requires the completed opening programme, independence, and readiness of at least 50 or an active war. This transition can occur only once.','TFR_EST_lift_nato_restrictions = yes',cost=50,available='has_country_flag = TFR_EST_opening_complete is_subject = no OR = { check_variable = { TFR_EST_readiness > 49 } has_war = yes }',visible='NOT = { has_country_flag = TFR_EST_nato_restrictions_lifted }',icon='generic_prepare_civil_war',ai=5,fire_once=True)
D('TFR_EST_defence_programmes','procure_infantry','A Limited Infantry Equipment Contract','Order 500 sets of basic infantry equipment from the domestic production base. Costs 50 political power and €40 million in public debt. Requires the procurement plan and an Estonian military factory. The 365-day cooldown limits deliveries.',reward(budget(40),'add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 500 producer = EST }'),cost=50,cooldown=365,available='has_country_flag = TFR_EST_procurement_plan num_of_military_factories > 0',visible='has_country_flag = TFR_EST_procurement_plan',icon='generic_prepare_civil_war',ai=2)
D('TFR_EST_defence_programmes','logistics_rehearsal','Rehearse Wartime Distribution','Fund a joint military and municipal transport exercise. Costs 35 political power and €25 million in public debt; increases readiness by 2 and grants 5 army experience. Available every 180 days.',reward(budget(25),rd(2),xp(5)),available='has_completed_focus = TFR_EST_logistics_audit',icon='generic_prepare_civil_war',ai=2)
decisions_text=''.join(cat+' = {\n'+''.join(vals)+'}\n\n' for cat,vals in decisions.items())

rule='''TFR_EST_AI_ROUTE = {
 name = TFR_EST_AI_ROUTE
 group = RULE_GROUP_AI_BEHAVIOR
 default = { name = DEFAULT text = TFR_EST_RULE_DEFAULT desc = TFR_EST_RULE_DEFAULT_DESC }
'''
L('TFR_EST_AI_ROUTE','Estonia: Preferred Campaigning Party')
L('TFR_EST_RULE_DEFAULT','Competitive Parliamentary Politics')
L('TFR_EST_RULE_DEFAULT_DESC','The opening 57-seat Ratas coalition is preserved. Subsequent coalition leadership goes to the party with the most elected seats; negotiations determine partners and confidence.')
for suffix,pid,label in parties:
    option=suffix.upper()
    L('TFR_EST_RULE_'+option,label)
    L('TFR_EST_RULE_'+option+'_DESC',f'AI Estonia favors {label} when campaigning for later elections. The chosen party must win the most seats before it can lead a coalition; this rule cannot override the electoral mandate. The historical opening coalition and parliamentary majority requirements remain intact. Parempoolsed becomes eligible only after its formation.')
    rule+=f' option = {{ name = {option} text = TFR_EST_RULE_{option} desc = TFR_EST_RULE_{option}_DESC }}\n'
rule+='}\n'

plans=''
for suffix,pid,label in parties:
    route_focuses=[f[0] for f in focuses if f[2]==pid]
    shared_order=['reserve_register','logistics_audit','allied_liaison','kaitseliit_training','interoperability','reserve_training_exercise','industrial_survey','tallinn_industry']
    # Unavailable entries are skipped: reactive campaign content takes priority as soon as its stage opens.
    emergency_order=[node[0] for node in second]+[node[0] for node in first]+[node[0] for node in restoration]+[node[0] for node in post]+[node[0] for node in interwar]
    order=['TFR_EST_opening_'+p.suffix for p in POLICIES]+[P+s for s in emergency_order]+['TFR_EST_ratas_'+p.suffix for p in RATAS_POLICIES]+['TFR_EST_kallas_'+p.suffix for p in KALLAS_POLICIES]+[P+s for s in shared_order]+route_focuses+[P+s for s in ['reserve_depots','mobilization_plans','realistic_procurement','total_defence','prepared_alliance','national_supply_plan','prepared_positions','artillery_observers','air_defence_integration']]
    L(P+suffix+'_ai_plan',f'Estonia: {label} Governing Programme')
    plans+=f'''TFR_EST_{suffix}_ai_plan = {{
 name = TFR_EST_{suffix}_ai_plan
 desc = ""
 allowed = {{ original_tag = EST }}
 enable = {{ check_variable = {{ TFR_EST_pm_party = {pid} }} NOT = {{ has_country_flag = TFR_EST_occupied }} NOT = {{ has_country_flag = TFR_EST_caretaker }} }}
 abort = {{ OR = {{ NOT = {{ check_variable = {{ TFR_EST_pm_party = {pid} }} }} has_country_flag = TFR_EST_occupied has_country_flag = TFR_EST_caretaker }} }}
 ai_national_focuses = {{ {' '.join(order)} }}
 focus_factors = {{ TFR_EST_first_emergency = 15 TFR_EST_second_emergency = 15 TFR_EST_restored_authority = 15 }}
 weight = {{ factor = 1.0 }}
}}\n\n'''
strategy='''TFR_EST_territorial_force = {
 enable = { original_tag = EST NOT = { has_country_flag = TFR_EST_occupied } }
 abort = { has_country_flag = TFR_EST_occupied }
 ai_strategy = { type = unit_ratio id = infantry value = 30 }
 ai_strategy = { type = unit_ratio id = artillery value = 10 }
 ai_strategy = { type = unit_ratio id = anti_air value = 10 }
 ai_strategy = { type = unit_ratio id = armor value = -50 }
}
'''

def write(rel,text,bom=False):
    if args.focus_only and rel not in {
        'common/national_focus/TFR_EST_normal.txt',
        'common/ai_strategy_plans/TFR_EST_governments.txt',
        'common/decisions/TFR_EST_content.txt',
        'localisation/english/TFR_EST_content_l_english.yml',
    }:
        return
    text = native_amount_calls(text)
    # Explicit equality gates avoid relying on shorthand compare defaults in the engine.
    text = re.sub(r'check_variable\s*=\s*\{\s*(TFR_EST_\w+)\s*=\s*(-?\d+(?:\.\d+)?)\s*\}',
                  lambda m: f'check_variable = {{ var = {m.group(1)} value = {m.group(2)} compare = equals }}', text)
    path=ROOT/rel;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8-sig' if bom else 'utf-8',newline='\n')

write('common/national_focus/TFR_EST_normal.txt',tree)
write('common/ideas/TFR_EST_content.txt',ideas_text)
write('common/scripted_effects/TFR_EST_content.txt',effects)
write('common/decisions/categories/TFR_EST_content.txt',categories)
write('common/decisions/TFR_EST_content.txt',decisions_text)
write('events/TFR_EST_content.txt',events_text)
write('common/game_rules/TFR_EST_routes.txt',rule)
write('common/ai_strategy_plans/TFR_EST_governments.txt',plans)
write('common/ai_strategy/TFR_EST_content.txt',strategy)
loc_text='l_english:\n'+''.join(' '+key+':0 '+json.dumps(value,ensure_ascii=False)+'\n' for key,value in loc.items())
write('localisation/english/TFR_EST_content_l_english.yml',loc_text,True)
print(f'Wrote {len(focuses)} normal focuses, {len(events)} choice events, {sum(map(len,decisions.values()))} decisions, {len(ideas)} spirits and {len(loc)} localization keys.')
