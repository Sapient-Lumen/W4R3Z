// CloudtainerML rev0042 — observable blockwise index branch refactor.
//
// rev0039 used a synthetic score that directly rewarded the hidden target block.
// This pass separates hidden target labels from observable selector features. It
// remains an E1 toy, but selection now uses simulated observable summaries only:
// local prior, query-phase similarity, boundary anchors, group offsets, and noise.
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

using namespace std;

#ifndef SOURCE_SHA256
#define SOURCE_SHA256 "unknown"
#endif
#ifndef BUILD_COMMAND
#define BUILD_COMMAND "unknown"
#endif

struct Item {
    int block;
    int group;
    double observable_score;
    double query_phase_score;
    double local_prior;
    double boundary_prior;
    bool target;
    bool local;
    bool distractor;
};

struct Row {
    string regime, method;
    int seed, selected_blocks, group_count, block_budget, exact_hit, target_blocks, false_blocks;
    double recall, target_miss, block_cost, selector_cost, wall_proxy, regret, rank_quality, score;
    double local_anchor, boundary_anchor, output_quality_proxy, observable_target_gap;
};

static string q(const string& s){
    string o="\"";
    for(char c:s){ if(c=='\"'||c=='\\'){o+='\\'; o+=c;} else if(c=='\n') o+="\\n"; else o+=c; }
    o+='\"'; return o;
}
static double clamp01(double x){ return max(0.0,min(1.0,x)); }
static double wrap_dist(int a, int b, int n){ int d=abs(a-b); return min(d,n-d); }
static vector<int> topk_indices(const vector<double>& scores, int k){
    vector<int> idx(scores.size()); iota(idx.begin(), idx.end(), 0);
    stable_sort(idx.begin(), idx.end(), [&](int a,int b){ if(scores[a]!=scores[b]) return scores[a]>scores[b]; return a<b; });
    if((int)idx.size()>k) idx.resize(k); return idx;
}

struct RegimeSpec { string name; int phase_offset; double feature_noise; double distractor_strength; double local_weight; double boundary_weight; };

static vector<Item> make_items(const RegimeSpec& regime, int seed, int blocks=32, int groups=4){
    mt19937 rng(seed * 1009 + (int)regime.name.size() * 17);
    normal_distribution<double> noise(0.0, regime.feature_noise);
    vector<Item> xs; xs.reserve(blocks*groups);
    for(int g=0; g<groups; ++g){
        int local = blocks-1;
        // Observable query-phase signal. It is not the target label; hidden target
        // can be offset, aliased, or weakened by regime.
        int query_phase = (seed*7 + g*11 + (int)regime.name.size()*3) % blocks;
        int target = (query_phase + regime.phase_offset + blocks) % blocks;
        if(regime.name=="local_easy") target=local;
        if(regime.name=="boundary_bridge") target=max(1, (query_phase/4)*4);
        if(regime.name=="far_sparse_needle") target=(query_phase + blocks/2 + 3*g) % blocks;
        if(regime.name=="group_specific") target=(query_phase + g*5 + 3) % blocks;
        if(regime.name=="offphase_alias") target=(query_phase + (g%2 ? 8 : -8) + blocks) % blocks;
        if(regime.name=="distractor_blocks") target=(query_phase + 3 + g) % blocks;
        for(int b=0;b<blocks;++b){
            bool is_target=(b==target);
            bool is_local=(b==local);
            bool is_boundary=(b%4==3);
            bool is_distractor=false;
            double phase = 1.0 - wrap_dist(b, query_phase, blocks) / (blocks/2.0);
            double local_prior = is_local ? 1.0 : 0.0;
            double boundary_prior = is_boundary ? 1.0 : 0.0;
            double group_offset = 0.08 * cos((b + 3*g + seed%13) * 0.37);
            double score = 0.10 + 0.58*phase + regime.local_weight*local_prior + regime.boundary_weight*boundary_prior + group_offset + noise(rng);
            if(regime.name=="smooth_long_context") score += 0.22*cos((b - query_phase)*3.14159/blocks);
            if(regime.name=="distractor_blocks" && b!=target && ((b+seed+g)%5==0)){ score += regime.distractor_strength; is_distractor=true; }
            if(regime.name=="offphase_alias" && b!=target && abs(b-query_phase)%8==0){ score += regime.distractor_strength; is_distractor=true; }
            if(regime.name=="far_sparse_needle" && is_target) score -= 0.14; // hidden hard case, not a selector bonus.
            xs.push_back({b,g,score,phase,local_prior,boundary_prior,is_target,is_local,is_distractor});
        }
    }
    return xs;
}

static set<pair<int,int>> select_method(const vector<Item>& xs, const string& method, int groups, int blocks, int budget){
    set<pair<int,int>> sel;
    if(method=="dense_full"){
        for(auto& it:xs) sel.insert({it.group,it.block}); return sel;
    }
    if(method=="local_block_only"){
        for(int g=0; g<groups; ++g) sel.insert({g,blocks-1}); return sel;
    }
    if(method=="shared_observable_index_once"){
        vector<double> agg(blocks,0.0);
        for(auto& it:xs) agg[it.block]+=it.observable_score;
        auto ids=topk_indices(agg,max(1,budget));
        for(int g=0; g<groups; ++g){ sel.insert({g,blocks-1}); for(int b:ids) sel.insert({g,b}); }
        return sel;
    }
    if(method=="group_observable_block_index"){
        for(int g=0; g<groups; ++g){
            vector<double> sc(blocks,-1e9);
            for(auto& it:xs) if(it.group==g) sc[it.block]=it.observable_score;
            auto ids=topk_indices(sc,max(1,budget));
            sel.insert({g,blocks-1}); for(int b:ids) sel.insert({g,b});
        }
        return sel;
    }
    if(method=="group_index_plus_boundary_prior"){
        for(int g=0; g<groups; ++g){
            vector<double> sc(blocks,-1e9);
            for(auto& it:xs) if(it.group==g) sc[it.block]=it.observable_score + 0.12*it.boundary_prior;
            auto ids=topk_indices(sc,max(1,budget));
            sel.insert({g,blocks-1});
            for(int boundary=4; boundary<blocks; boundary+=4) sel.insert({g,boundary-1});
            for(int b:ids) sel.insert({g,b});
        }
        return sel;
    }
    if(method=="token_oracle_upper"){
        for(auto& it:xs) if(it.target) sel.insert({it.group,it.block});
        return sel;
    }
    return sel;
}

static Row score_row(const vector<Item>& xs, const string& regime, const string& method, int seed, int groups, int blocks, int budget){
    auto sel=select_method(xs,method,groups,blocks,budget);
    int targets=0,hits=0,falseb=0, local=0, boundary=0;
    double target_score=0.0, non_target_score=0.0; int nt=0, nn=0;
    for(auto& it:xs){
        bool picked=sel.count({it.group,it.block});
        if(picked && it.target) hits++;
        if(picked && !it.target && !it.local && it.boundary_prior<0.5) falseb++;
        if(picked && it.local) local++;
        if(picked && it.boundary_prior>0.5) boundary++;
        if(it.target){ targets++; target_score += it.observable_score; nt++; }
        else { non_target_score += it.observable_score; nn++; }
    }
    double recall=(double)hits/max(1,targets);
    double miss=1.0-recall;
    double block_cost=(double)sel.size()/(groups*blocks);
    double selector_cost=0.0;
    if(method=="dense_full") selector_cost=0.00;
    else if(method=="local_block_only") selector_cost=0.01;
    else if(method=="shared_observable_index_once") selector_cost=0.055;
    else if(method=="group_observable_block_index") selector_cost=0.105;
    else if(method=="group_index_plus_boundary_prior") selector_cost=0.130;
    else if(method=="token_oracle_upper") selector_cost=0.30;
    double wall=block_cost + selector_cost + 0.004*falseb;
    double observable_gap=(target_score/max(1,nt)) - (non_target_score/max(1,nn));
    double output_quality=clamp01(recall - 0.030*falseb + 0.018*boundary - 0.12*miss);
    double score = 1.68*recall + 0.22*output_quality - 0.64*wall - 0.20*miss;
    double rank_quality=clamp01(recall - 0.025*falseb + 0.015*boundary + 0.08*observable_gap);
    return {regime,method,seed,(int)sel.size(),groups,budget,hits,targets,falseb,recall,miss,block_cost,selector_cost,wall,0.0,rank_quality,score,(double)local/groups,(double)boundary/groups,output_quality,observable_gap};
}

int main(int argc, char** argv){
    string out = argc>1 ? argv[1] : "artifacts/probe-results/REV0042_BLOCKWISE_INDEX_OBSERVABLE_SMOKE.json";
    vector<RegimeSpec> regimes={
        {"local_easy",0,0.055,0.00,0.50,0.02},
        {"boundary_bridge",0,0.060,0.00,0.10,0.24},
        {"far_sparse_needle",0,0.080,0.00,0.08,0.04},
        {"group_specific",2,0.070,0.00,0.10,0.04},
        {"offphase_alias",0,0.075,0.42,0.08,0.08},
        {"distractor_blocks",1,0.070,0.52,0.08,0.05},
        {"smooth_long_context",1,0.060,0.00,0.12,0.08}
    };
    vector<string> methods={"dense_full","local_block_only","shared_observable_index_once","group_observable_block_index","group_index_plus_boundary_prior","token_oracle_upper"};
    vector<Row> rows;
    int blocks=32,groups=4;
    for(auto& regime: regimes){
        for(int budget: {1,2,3,5}){
            for(int seed=11; seed<31; seed+=4){
                auto xs=make_items(regime,seed,blocks,groups);
                vector<Row> tmp;
                for(auto& m:methods) tmp.push_back(score_row(xs,regime.name,m,seed,groups,blocks,budget));
                double best=-1e9; for(auto& r:tmp) if(r.score>best) best=r.score;
                for(auto& r:tmp){ r.regret=best-r.score; rows.push_back(r); }
            }
        }
    }
    map<string,int> wins, nonoracle;
    map<string,double> recall_sum, wall_sum, quality_sum, regret_sum; map<string,int> counts;
    for(size_t i=0;i<rows.size();){
        size_t j=i; while(j<rows.size() && rows[j].regime==rows[i].regime && rows[j].seed==rows[i].seed && rows[j].block_budget==rows[i].block_budget) j++;
        auto best=max_element(rows.begin()+i, rows.begin()+j, [](const Row&a,const Row&b){return a.score<b.score;});
        wins[best->method]++;
        auto best2=max_element(rows.begin()+i, rows.begin()+j, [](const Row&a,const Row&b){
            auto ao=(a.method.find("oracle")!=string::npos), bo=(b.method.find("oracle")!=string::npos);
            double as=ao?-1e9:a.score, bs=bo?-1e9:b.score; return as<bs;
        });
        if(best2!=rows.begin()+j) nonoracle[best2->method]++;
        for(size_t k=i;k<j;k++){
            recall_sum[rows[k].method]+=rows[k].recall; wall_sum[rows[k].method]+=rows[k].wall_proxy;
            quality_sum[rows[k].method]+=rows[k].output_quality_proxy; regret_sum[rows[k].method]+=rows[k].regret; counts[rows[k].method]++;
        }
        i=j;
    }
    ofstream f(out); f << fixed << setprecision(6);
    f << "{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\"rev0042\",\n  \"probe\":\"blockwise_index_branch_observable\",\n  \"kind\":\"native_cxx_probe\",\n";
    f << "  \"source_ids\":[\"SRC-0358\",\"SRC-0359\",\"SRC-0361\"],\n  \"cell_ids\":[\"CELL-353\"],\n";
    f << "  \"repair_of\":\"rev0039_privileged_target_score_block_selector\",\n";
    f << "  \"run_provenance\":{\"source_path\":\"experiments/blockwise_index_branch/blockwise_index_branch.cpp\",\"source_sha256\":"<<q(SOURCE_SHA256)<<",\"build_command\":"<<q(BUILD_COMMAND)<<",\"selector_policy\":\"selection uses observable_score/query-phase/local/boundary features only; target labels are used only for evaluation and token_oracle_upper\"},\n";
    f << "  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"higher_is_better\"},\n    \"winner_counts\":{";
    bool first=true; for(auto& kv:wins){ if(!first) f<<","; first=false; f<<q(kv.first)<<":"<<kv.second; } f << "},\n    \"nonoracle_winner_counts\":{"; first=true; for(auto& kv:nonoracle){ if(!first) f<<","; first=false; f<<q(kv.first)<<":"<<kv.second; } f << "},\n";
    auto dump_mean=[&](const map<string,double>& sums){ bool first2=true; f<<"{"; for(auto& kv:sums){ if(!first2) f<<","; first2=false; f<<q(kv.first)<<":"<<(kv.second/max(1,counts[kv.first])); } f<<"}"; };
    f << "    \"mean_recall\":"; dump_mean(recall_sum); f << ",\n";
    f << "    \"mean_wall_proxy\":"; dump_mean(wall_sum); f << ",\n";
    f << "    \"mean_output_quality_proxy\":"; dump_mean(quality_sum); f << ",\n";
    f << "    \"mean_regret\":"; dump_mean(regret_sum); f << ",\n";
    f << "    \"guard_fields\":[\"target_miss\",\"recall\",\"block_cost\",\"selector_cost\",\"wall_proxy\",\"false_blocks\",\"local_anchor\",\"boundary_anchor\",\"output_quality_proxy\",\"observable_target_gap\",\"regret\"],\n    \"interpretation\":\"rev0042 removes the direct target-score leak from the block-index toy. Block selectors now use observable synthetic features; target labels evaluate recall/output-quality only. This is still E1 synthetic evidence, not a speed or attention-kernel claim.\"\n  },\n  \"rows\":[\n";
    for(size_t i=0;i<rows.size();++i){ auto&r=rows[i];
        f << "    {\"regime\":"<<q(r.regime)<<",\"method\":"<<q(r.method)<<",\"seed\":"<<r.seed<<",\"block_budget\":"<<r.block_budget<<",\"selected_blocks\":"<<r.selected_blocks<<",\"group_count\":"<<r.group_count<<",\"exact_hit\":"<<r.exact_hit<<",\"target_blocks\":"<<r.target_blocks<<",\"false_blocks\":"<<r.false_blocks<<",\"recall\":"<<r.recall<<",\"target_miss\":"<<r.target_miss<<",\"block_cost\":"<<r.block_cost<<",\"selector_cost\":"<<r.selector_cost<<",\"wall_proxy\":"<<r.wall_proxy<<",\"rank_quality\":"<<r.rank_quality<<",\"local_anchor\":"<<r.local_anchor<<",\"boundary_anchor\":"<<r.boundary_anchor<<",\"output_quality_proxy\":"<<r.output_quality_proxy<<",\"observable_target_gap\":"<<r.observable_target_gap<<",\"regret\":"<<r.regret<<",\"score\":"<<r.score<<"}" << (i+1==rows.size()?"\n":" ,\n");
    }
    f << "  ]\n}\n";
    cerr << "wrote " << out << " rows="<<rows.size()<<"\n";
    return 0;
}
