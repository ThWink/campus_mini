FROM docker.m.daocloud.io/eclipse-temurin:17-jdk AS build
WORKDIR /workspace
COPY . .
RUN if [ ! -f src/main/resources/application.yaml ] && [ -f src/main/resources/application.example.yaml ]; then \
      cp src/main/resources/application.example.yaml src/main/resources/application.yaml; \
    fi
RUN chmod +x ./mvnw && ./mvnw -DskipTests package

FROM docker.m.daocloud.io/eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /workspace/target/runner-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
