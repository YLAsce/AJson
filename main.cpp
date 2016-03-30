#include "sample.h"
#include <iostream>
#include <fstream>
#include <cstring>

using namespace std;

class A
{
public:
    A(){

    }

    int a = 10;
};

int main()
{
	/*Sample s("sample.json");
	cout<<s.getUserid()<<endl;
	cout<<s.getUsername()<<endl;
	cout<<s.getGames()[0]<<endl;
	cout<<s.getVerified()<<endl;
	cout<<s.getWeight()<<endl;
	cout<<s.getItems().size()<<endl;
	cout<<s.getC()[0].getName()<<endl;
	*/
	A a;
	cout<<a.a;
	return 0;
}
