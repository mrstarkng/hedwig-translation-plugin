/* eslint-disable no-undef */
const path = require("path");
const devCerts = require("office-addin-dev-certs");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const HtmlWebpackPlugin = require("html-webpack-plugin");

const urlDev = "https://localhost:3000/";
const urlProd = "https://your-production-url.com/"; // <-- Đổi thành domain thật khi deploy

async function getHttpsOptions() {
  const httpsOptions = await devCerts.getHttpsServerOptions();
  return {
    ca: httpsOptions.ca,
    key: httpsOptions.key,
    cert: httpsOptions.cert,
  };
}

module.exports = async (env, options) => {
  const dev = options.mode === "development";

  return {
    devtool: "source-map",
    entry: {
  polyfill: ["core-js/stable", "regenerator-runtime/runtime"],
  taskpane: "./src/taskpane/taskpane.js", 
  commands: "./src/commands/commands.js",
},

 output: {
  clean: true,
  publicPath: "/", // hoặc "/hedwig/" nếu bạn host ở thư mục con
},

    resolve: {
      extensions: [".js", ".html"],
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
          },
        },
        {
          test: /\.html$/,
          use: "html-loader",
        },
        {
          test: /\.(png|jpg|jpeg|gif|ico)$/,
          type: "asset/resource",
          generator: {
            filename: "assets/[name][ext]",
          },
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({
        filename: "taskpane.html",
        template: "./src/taskpane/taskpane.html",
        chunks: ["polyfill", "taskpane"],
      }),
      new HtmlWebpackPlugin({
        filename: "commands.html",
        template: "./src/commands/commands.html",
        chunks: ["polyfill", "commands"],
      }),
      new CopyWebpackPlugin({
    patterns: [
   {
    from: "assets",
    to: "assets",
    globOptions: {
      ignore: ["**/.DS_Store"], // tránh lỗi trên macOS
    },
  },

          {
            from: "manifest.xml",
            to: "manifest.xml",
            transform(content) {
              return dev
                ? content
                : content.toString().replace(new RegExp(urlDev, "g"), urlProd);
            },
          },
        ],
      }),
    ],
    devServer: {
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
      server: {
        type: "https",
        options: await getHttpsOptions(),
      },
      port: process.env.npm_package_config_dev_server_port || 3000,
    },
  };
};

console.log("✅ ĐANG DÙNG FILE WEBPACK NÀY:", __filename);
