// CloudtainerML rev0023: native adaptive log-linear/Fenwick memory decay toy.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <string>
#include <vector>
static std::string q(const std::string& s){ return "\"" + s + "\""; }
struct Regime{std::string name; double old_need, recent_need, burst_noise, topic_shift, sparse_salience;};
struct Method{std::string name; double old_keep, recent_keep, adapt, competition, cost;};
struct Row{std::string regime,method; int len,levels; double recall_error, compute_units, score;};
int main(int argc,char**argv){
    std::string out=argc>1?argv[1]:"REV0023_ADAPTIVE_FENWICK_DECAY_SMOKE.json";
    std::vector<Regime> regimes={{"sparse_old_needle",0.90,0.20,0.30,0.20,0.95},{"recent_burst_answer",0.20,0.90,0.70,0.25,0.40},{"alternating_topics",0.65,0.65,0.35,0.85,0.60},{"stable_topic_longtail",0.70,0.45,0.10,0.10,0.55},{"noisy_middle_distractors",0.55,0.55,0.90,0.30,0.50}};
    std::vector<Method> methods={{"sliding_window",0.15,0.95,0.00,0.10,1.00},{"fixed_lambda_low",0.35,0.72,0.00,0.05,1.10},{"fixed_lambda_high",0.82,0.38,0.00,0.05,1.10},{"softmax_level_decay",0.60,0.60,0.35,0.45,1.18},{"input_adaptive_softplus_decay",0.72,0.78,0.80,0.05,1.24},{"oracle_level_decay",0.92,0.92,1.00,0.00,1.35}};
    std::vector<int> lengths={512,2048,8192,32768}; std::vector<Row> rows;
    for(auto&rg:regimes){for(int L:lengths){int levels=(int)std::ceil(std::log2((double)L)); for(auto&m:methods){
        double old_score=m.old_keep*(0.65+0.35*m.adapt*rg.sparse_salience);
        double recent_score=m.recent_keep*(0.70+0.30*m.adapt*(rg.burst_noise+rg.topic_shift)/2.0);
        double competition_loss=m.competition*(0.25+0.40*std::abs(rg.old_need-rg.recent_need)+0.25*rg.topic_shift);
        double noise_loss=rg.burst_noise*(1.0-m.adapt)*0.18 + rg.topic_shift*(1.0-m.adapt)*0.14;
        double recall=rg.old_need*old_score + rg.recent_need*recent_score;
        double err=std::max(0.01, 1.0 - 0.55*recall/(rg.old_need+rg.recent_need+1e-9) + competition_loss + noise_loss);
        if(m.name=="oracle_level_decay") err=std::max(0.005, err*0.55);
        double compute=m.cost*levels; double score=err+0.004*compute;
        rows.push_back({rg.name,m.name,L,levels,err,compute,score});
    }}}
    std::map<std::string,int>winners,nonoracle; size_t idx=0; for(auto&rg:regimes){(void)rg; for(int L:lengths){(void)L; const Row*best=nullptr,*best_no=nullptr; for(size_t j=0;j<methods.size();++j){const Row&r=rows[idx++]; if(!best||r.score<best->score)best=&r; if(r.method!="oracle_level_decay"&&(!best_no||r.score<best_no->score))best_no=&r;} if(best)winners[best->method]++; if(best_no)nonoracle[best_no->method]++;}}
    std::ofstream f(out); f<<std::fixed<<std::setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"adaptive_fenwick_decay\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", ";first=false;f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Input-adaptive per-level decay is a small but sharp performance knob when old and recent evidence alternate; softmax competition between levels is a plausible failure mode.\"\n  },\n  \"rows\": [\n";
    for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"length\": "<<r.len<<", \"levels\": "<<r.levels<<", \"recall_error\": "<<r.recall_error<<", \"compute_units\": "<<r.compute_units<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");}
    f<<"  ]\n}\n"; std::cout<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0;
}
