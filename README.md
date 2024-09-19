# Vines 🌿

**Vines** is a lightweight, high-performance Python web framework built on the ASGI standard.
Currently under **active development**, Vines is designed for the rapid creation of RESTful APIs.
While it's evolving, developers are encouraged to explore, contribute, and share feedback.


## 🚧 Project Status

* **Status:** Pre-release v0.1.0
* **First Stable Release:** v1.0.0

Vines is in an early stage of development.
Core features are being built and refined, and the API is subject to change.
Your contributions and suggestions are highly welcome!


## 🏁 Getting Started

### 🔧 Installation

Since Vines is in development, install it directly from the repository using pip:

```bash
pip install git+https://github.com/spyel/vines.git
```

Alternatively, clone the repository and install it locally:

```bash
git clone https://github.com/spyel/vines.git
cd vines
pip install .
```

Additionally, you'll need an ASGI server like ``uvicorn``, ``daphne``, or ``hypercorn``:

```bash
pip install uvicorn
```

### 🖥️ Running a Basic Application

Here's an example to help you get started with a basic Vines application:

```python
import uvicorn
from vines import Vines
from vines.http import JSONResponse

app = Vines()

@app.route('/')
def home(request):
    return JSONResponse({'message': 'Welcome to Vines!'})
    
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
```

Once the server is running, visit ```http://127.0.0.1:8000``` to see your basic Vines application in action.


## 📄 License

Vines is licensed under the [MIT License](LICENSE).


## 👥 Community and Support

If you have any questions or need support, feel free to:

* **Open an Issue:** Use [GitHub Issues](https://github.com/spyel/vines/issues) to ask questions or report bugs.
* **Join the Discussion:** Engage with the community in our [forum](https://github.com/spyel/vines/discussions).


Thank you for exploring Vines!
Your feedback and contributions are crucial as we continue to build and enhance the framework.

Happy coding! 🎉