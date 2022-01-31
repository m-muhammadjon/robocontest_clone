#include<bits/stdc++.h>
using namespace std;
int main(){
	long long a[99], n, summ;
	cin>>n;
	a[1]=2;
	a[2]=2;
	if(n>2){
		for(int i=3;i<=n;i++)
			a[i]=a[i-1]+a[i-2];
		cout<<a[n];
	}
	else
		cout<<2;
}