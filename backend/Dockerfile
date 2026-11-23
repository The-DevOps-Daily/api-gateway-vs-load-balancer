FROM golang:1.27.4-alpine AS build
WORKDIR /src
COPY go.mod main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /backend .

FROM scratch
COPY --from=build /backend /backend
ENTRYPOINT ["/backend"]
