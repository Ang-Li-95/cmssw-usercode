#ifndef JMTucker_MFVNeutralino_One2Two_ProgressBar_h
#define JMTucker_MFVNeutralino_One2Two_ProgressBar_h

#include <string>

namespace jmt {
  class ProgressBar {
  private:
    const int n_dots;
    const int n_per_dot;
    const bool flush;
    const std::string chars;
    int i;
    int idot;

  public:
    ProgressBar(int n_dots_, int n_complete, bool flush_=true, const char* chars_="[ ].");
    void start();
    ProgressBar& operator++();
  };
}

#endif
