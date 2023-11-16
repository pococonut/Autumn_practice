#include <iostream>
#include <math.h>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <cmath>

using namespace std;

class Complex_num
{
private:
	float re_num, im_num;
public:

	// конструктор
	Complex_num()
	{
		re_num = 0;
		im_num = 0;
	}

	Complex_num(float re_num, float im_num)
	{
		this->re_num = re_num;
		this->im_num = im_num;
	}

	// деструктор
	~Complex_num() {}

	float Get_Compex_re_num() { return re_num; }
	float Get_Complex_im_num() { return im_num; }

	
	float complex_abs() {
		return sqrt((re_num * re_num) + (im_num * im_num));
	}

	// метод для возведения комплексного числа в степень
	Complex_num power(float exponent) {
		float magnitude = sqrt(re_num * re_num + im_num * im_num);
		float angle = atan2(im_num, re_num);

		float newMagnitude = pow(magnitude, exponent);
		float newAngle = angle * exponent;

		float newRe = newMagnitude * cos(newAngle);
		float newIm = newMagnitude * sin(newAngle);

		return Complex_num(newRe, newIm);
	}

	// перегрузка операторов
	
	Complex_num& operator +(const Complex_num& value)
	{
		/* this является указателем на текущий объект
		this->re_num и this->im_num используются для доступа к членам текущего объекта,
		а value.re_num и value.im_num - для доступа к членам объекта,
		переданного в качестве аргумента метода*/
		
		Complex_num result;
		result.re_num = this->re_num + value.re_num;
		result.im_num = this->im_num + value.im_num;
		return result;
	}

	Complex_num& operator -(const Complex_num& value)
	{
		Complex_num result;
		result.re_num = this->re_num - value.re_num;
		result.im_num = this->im_num - value.im_num;
		return result;
	}

	Complex_num& operator *(const Complex_num& value)
	{
		Complex_num result;
		if ((value.re_num == -1) && (value.im_num == -1))
		{
			result.re_num = this->re_num * -1;
			result.im_num = this->im_num * -1;
		}
		else {
			result.re_num = re_num * value.re_num - im_num * value.im_num;
			result.im_num = re_num * value.im_num + im_num * value.re_num;
		}
		return result;
	}

	Complex_num& operator /(const Complex_num& value)
	{
		Complex_num result;
		result.re_num = (re_num * value.re_num + im_num * value.im_num) / (pow(value.re_num, 2) + pow(value.im_num, 2));
		result.im_num = (im_num * value.re_num - re_num * value.im_num) / (pow(value.re_num, 2) + pow(value.im_num, 2));
		return result;
	}

	/*
	Перегрузка оператора вывода осуществляется с помощью функции, 
	которая принимает два аргумента: ссылку на объект ostream (поток вывода) 
	и константную ссылку на объект класса Complex_num, который нужно вывести.
	
	Ключевое слово "friend" перед объявлением функции означает, 
	что эта функция является дружественной функцией класса Complex_num. 
	Дружественная функция имеет доступ к закрытым (private) и защищенным (protected) членам класса, 
	включая приватные переменные и методы.
	*/

	friend ostream& operator <<(ostream& os, const Complex_num& value)
	{
		return cout << value.re_num << " + i" << value.im_num;
	}
};


int main() {
	setlocale(LC_ALL, "ru");

	int re_a1, im_a1;
	cout << "Введите реальную часть числа а1: ";
	cin >> re_a1;
	cout << "Введите мнимую часть числа а1: ";
	cin >> im_a1;

	int re_a2, im_a2;
	cout << "Введите реальную часть числа a2: ";
	cin >> re_a2;
	cout << "Введите мнимую часть числа a2: ";
	cin >> im_a2;

	int re_a3, im_a3;
	cout << "Введите реальную часть числа a3: ";
	cin >> re_a3;
	cout << "Введите мнимую часть числа a3: ";
	cin >> im_a3;
	cout << endl;

	Complex_num a1(re_a1, im_a1);
	cout << "a1: " << a1 << endl;
	Complex_num a2(re_a2, im_a2);
	cout << "a2: " << a2 << endl;
	Complex_num a3(re_a3, im_a3);
	cout << "a3: " << a3 << endl;
	cout << endl;

	Complex_num d1 = a2.power(4);
	cout << d1 << endl;

	Complex_num d2 = a1 - a2;
	cout << d2 << endl;

	Complex_num d3 = a3 * a1;
	cout << d3 << endl;

	Complex_num d4 = d2 / d3;
	cout << d4 << endl;

	Complex_num d5 = d4 + d1;
	cout << d5 << endl;
	cout << endl;

	float result = d5.complex_abs();
	cout << "result: " << result << endl;

}