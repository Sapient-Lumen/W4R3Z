#include <sqlite3.h>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include <cstring>
namespace fs=std::filesystem;
static void ck(int rc, sqlite3* db, const char* what){ if(rc!=SQLITE_OK){std::cerr<<what<<" rc="<<rc<<" msg="<<(db?sqlite3_errmsg(db):"")<<"\n"; std::exit(2);} }
int main(int argc,char**argv){
 fs::path p=argc>1?argv[1]:"/tmp/wal_deserialize_probe.sqlite";
 std::error_code ec; fs::remove(p,ec); fs::remove(p.string()+"-wal",ec); fs::remove(p.string()+"-shm",ec);
 sqlite3* w=nullptr; ck(sqlite3_open_v2(p.c_str(),&w,SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE|SQLITE_OPEN_FULLMUTEX,nullptr),w,"openw");
 ck(sqlite3_exec(w,"PRAGMA journal_mode=WAL; PRAGMA wal_autocheckpoint=0; CREATE TABLE t(v TEXT); INSERT INTO t VALUES('x'); PRAGMA wal_checkpoint(TRUNCATE);",nullptr,nullptr,nullptr),w,"setup");
 std::cout<<"before close wal="<<fs::exists(p.string()+"-wal")<<" shm="<<fs::exists(p.string()+"-shm")<<"\n";
 ck(sqlite3_close_v2(w),nullptr,"closew");
 std::cout<<"after close wal="<<fs::exists(p.string()+"-wal")<<" shm="<<fs::exists(p.string()+"-shm")<<" bytes="<<fs::file_size(p)<<"\n";
 std::ifstream in(p,std::ios::binary); std::vector<unsigned char> b((std::istreambuf_iterator<char>(in)),{});
 std::cout<<"header18="<<(int)b[18]<<" header19="<<(int)b[19]<<"\n";
 unsigned char* c=(unsigned char*)sqlite3_malloc64(b.size()); std::memcpy(c,b.data(),b.size());
 sqlite3* d=nullptr; ck(sqlite3_open_v2(":memory:",&d,SQLITE_OPEN_READONLY|SQLITE_OPEN_MEMORY|SQLITE_OPEN_PRIVATECACHE|SQLITE_OPEN_FULLMUTEX,nullptr),d,"opend");
 int rc=sqlite3_deserialize(d,"main",c,b.size(),b.size(),SQLITE_DESERIALIZE_FREEONCLOSE|SQLITE_DESERIALIZE_READONLY);
 std::cout<<"deserialize rc="<<rc<<" msg="<<sqlite3_errmsg(d)<<" readonly="<<sqlite3_db_readonly(d,"main")<<" filename='"<<(sqlite3_db_filename(d,"main")?:"<null>")<<"'\n";
 sqlite3_stmt* s=nullptr; rc=sqlite3_prepare_v2(d,"SELECT count(*) FROM t",-1,&s,nullptr); std::cout<<"prepare rc="<<rc<<" msg="<<sqlite3_errmsg(d)<<"\n"; if(rc==SQLITE_OK){rc=sqlite3_step(s); std::cout<<"step rc="<<rc<<" val="<<(rc==SQLITE_ROW?sqlite3_column_int(s,0):-1)<<" msg="<<sqlite3_errmsg(d)<<"\n"; sqlite3_finalize(s);} 
 sqlite3_close_v2(d);
}
