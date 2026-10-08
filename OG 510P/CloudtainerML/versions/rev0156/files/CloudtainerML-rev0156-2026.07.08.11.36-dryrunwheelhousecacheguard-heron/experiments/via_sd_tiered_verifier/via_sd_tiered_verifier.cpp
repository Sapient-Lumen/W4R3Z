// CloudtainerML rev0027 — VIA-SD-style tiered verifier speculative decoding toy.
// Performance/cost wind tunnel; not an implementation of any LLM inference stack.
#include <bits/stdc++.h>
using namespace std; static string q(const string&s){string o="\"";for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o+'"';}
struct Regime{string name; double draft_quality, confidence_calibration, medium_band, hard_tail, burst_errors;};
struct Method{string name; double direct, slim, full, calibration, overhead, quality_guard; bool oracle=false;};
struct Row{string regime, method; int block; double accept, mismatch, cost, speedup, score, full_calls;};
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0027_VIA_SD_TIERED_VERIFIER_SMOKE.json";
 vector<Regime> regimes={{"easy_draft",0.92,0.86,0.35,0.05,0.03},{"bimodal_confidence",0.76,0.62,0.76,0.14,0.08},{"noisy_draft",0.58,0.42,0.52,0.32,0.18},{"medium_confidence_heavy",0.70,0.55,0.92,0.18,0.10},{"hard_tail_tokens",0.74,0.70,0.50,0.70,0.12},{"bursty_rejections",0.68,0.58,0.58,0.24,0.72}};
 vector<Method> methods={{"binary_accept_full",0.62,0.00,1.00,0.60,0.02,0.92,false},{"direct_confidence_only",0.82,0.00,0.42,0.45,0.01,0.45,false},{"slim_all_rejects",0.54,0.88,0.35,0.58,0.09,0.62,false},{"via_sd_three_tier",0.68,0.76,0.55,0.82,0.11,0.82,false},{"aggressive_slim_tier",0.78,0.82,0.28,0.62,0.10,0.60,false},{"conservative_slim_tier",0.58,0.70,0.78,0.88,0.12,0.92,false},{"oracle_tier",0.90,0.92,0.44,1.00,0.15,1.00,true}};
 vector<int> blocks={4,8,12,16}; vector<Row> rows; map<string,int>winners,nonoracle;
 for(auto&rg:regimes) for(int B:blocks){vector<Row>cand; for(auto&m:methods){
   double draft_accept=rg.draft_quality*m.direct*(0.82+0.18*rg.confidence_calibration*m.calibration);
   double medium_rescue=rg.medium_band*m.slim*(0.35+0.55*m.calibration)*(0.75+0.25*rg.draft_quality);
   double hard_pen=rg.hard_tail*(0.35*(1.0-m.full)+0.18*(1.0-m.quality_guard));
   double burst_pen=rg.burst_errors*(0.25*(1.0-m.full)+0.15*(1.0-m.calibration))*log2((double)B)/4.0;
   double accept=min(0.98,max(0.0,draft_accept+0.32*medium_rescue-0.18*hard_pen-0.12*burst_pen));
   double mismatch=max(0.0001,0.020 + hard_pen + burst_pen + (1.0-rg.confidence_calibration)*(0.12*(1.0-m.calibration)) - 0.08*m.quality_guard);
   double full_calls=max(0.02, (1.0-m.direct)*0.55 + (1.0-m.slim)*0.18 + m.full*0.22 + rg.hard_tail*0.20 + rg.burst_errors*0.18);
   double slim_calls=max(0.0, rg.medium_band*m.slim*0.55);
   double cost=(full_calls*1.0 + slim_calls*0.24 + m.overhead + 0.015*B)/(double)B;
   if(m.oracle){accept=min(0.995,0.86+0.09*rg.draft_quality); mismatch=0.006+0.015*rg.hard_tail; cost*=0.72; full_calls*=0.55;}
   double speedup=1.0/max(0.08,cost);
   double score=cost + 5.5*mismatch + 0.24*(1.0-accept);
   cand.push_back({rg.name,m.name,B,accept,mismatch,cost,speedup,score,full_calls});
 }
 auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[best->method]++;
 auto bestNo=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){ if(a.method=="oracle_tier") return false; if(b.method=="oracle_tier") return true; return a.score<b.score;}); nonoracle[bestNo->method]++; rows.insert(rows.end(),cand.begin(),cand.end());}
 ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0027\",\n  \"probe\": \"via_sd_tiered_verifier\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Tiered verification only pays when medium-confidence tokens are common and slim verifier calibration is good; otherwise binary full verification or conservative tiers remain hard baselines.\",\n    \"screen_regret_fields\": [\"mismatch_rate\", \"expected_cost\", \"full_call_fraction\"]\n  },\n  \"rows\": [\n";
 for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"block\": "<<r.block<<", \"accept_rate\": "<<r.accept<<", \"mismatch_rate\": "<<r.mismatch<<", \"expected_cost\": "<<r.cost<<", \"speedup_proxy\": "<<r.speedup<<", \"full_call_fraction\": "<<r.full_calls<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
 f<<"  ]\n}\n"; cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
}
