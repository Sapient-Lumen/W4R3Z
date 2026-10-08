#include <fcntl.h>
#include <unistd.h>
#include <filesystem>
#include <cstdio>
#include <cerrno>
#include <cstring>
int main(){std::filesystem::path r="/tmp/anonsync-nofollow-check"; std::filesystem::remove_all(r); std::filesystem::create_directories(r/"real"); std::filesystem::create_directory_symlink("real",r/"link"); int flags=O_RDONLY; 
#ifdef O_DIRECTORY
flags|=O_DIRECTORY;
#endif
#ifdef O_NOFOLLOW
flags|=O_NOFOLLOW;
#endif
int fd=open((r/"link").c_str(),flags); printf("flags=%x fd=%d errno=%d %s\n",flags,fd,errno,strerror(errno)); if(fd>=0)close(fd);}
